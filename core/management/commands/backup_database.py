import os
import subprocess
import zipfile
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.management import call_command
import tempfile


class Command(BaseCommand):
    help = 'Cria backup do banco de dados e arquivos de mídia'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='backups',
            help='Diretório para salvar os backups'
        )
        parser.add_argument(
            '--include-media',
            action='store_true',
            help='Incluir arquivos de mídia no backup'
        )
        parser.add_argument(
            '--compress',
            action='store_true',
            help='Comprimir o backup em arquivo ZIP'
        )

    def handle(self, *args, **options):
        output_dir = options['output_dir']
        include_media = options['include_media']
        compress = options['compress']
        
        # Criar diretório de backup se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        # Timestamp para nome do arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Backup do banco de dados
        db_backup_file = os.path.join(output_dir, f'db_backup_{timestamp}.json')
        self.stdout.write(f'Criando backup do banco de dados: {db_backup_file}')
        
        with open(db_backup_file, 'w') as f:
            call_command('dumpdata', stdout=f, indent=2)
        
        self.stdout.write(
            self.style.SUCCESS(f'Backup do banco criado: {db_backup_file}')
        )
        
        # Backup dos arquivos de mídia
        if include_media and hasattr(settings, 'MEDIA_ROOT'):
            media_backup_dir = os.path.join(output_dir, f'media_backup_{timestamp}')
            self.stdout.write(f'Criando backup dos arquivos de mídia: {media_backup_dir}')
            
            # Copiar arquivos de mídia
            if os.path.exists(settings.MEDIA_ROOT):
                subprocess.run([
                    'cp', '-r', settings.MEDIA_ROOT, media_backup_dir
                ], check=True)
                
                self.stdout.write(
                    self.style.SUCCESS(f'Backup de mídia criado: {media_backup_dir}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Diretório de mídia não encontrado')
                )
        
        # Comprimir backup
        if compress:
            zip_file = os.path.join(output_dir, f'backup_{timestamp}.zip')
            self.stdout.write(f'Comprimindo backup: {zip_file}')
            
            with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Adicionar backup do banco
                zipf.write(db_backup_file, os.path.basename(db_backup_file))
                
                # Adicionar backup de mídia se incluído
                if include_media and os.path.exists(media_backup_dir):
                    for root, dirs, files in os.walk(media_backup_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, media_backup_dir)
                            zipf.write(file_path, f'media/{arcname}')
            
            # Remover arquivos temporários
            os.remove(db_backup_file)
            if include_media and os.path.exists(media_backup_dir):
                subprocess.run(['rm', '-rf', media_backup_dir], check=True)
            
            self.stdout.write(
                self.style.SUCCESS(f'Backup comprimido criado: {zip_file}')
            )
        
        # Limpar backups antigos (manter apenas os últimos 7 dias)
        self.cleanup_old_backups(output_dir)
        
        self.stdout.write(
            self.style.SUCCESS('Backup concluído com sucesso!')
        )

    def cleanup_old_backups(self, backup_dir):
        """Remove backups mais antigos que 7 dias"""
        import time
        
        current_time = time.time()
        seven_days_ago = current_time - (7 * 24 * 60 * 60)
        
        for filename in os.listdir(backup_dir):
            file_path = os.path.join(backup_dir, filename)
            if os.path.isfile(file_path):
                file_time = os.path.getmtime(file_path)
                if file_time < seven_days_ago:
                    os.remove(file_path)
                    self.stdout.write(f'Backup antigo removido: {filename}')
