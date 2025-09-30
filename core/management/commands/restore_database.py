import os
import zipfile
import tempfile
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Restaura backup do banco de dados e arquivos de mídia'

    def add_arguments(self, parser):
        parser.add_argument(
            'backup_file',
            type=str,
            help='Caminho para o arquivo de backup'
        )
        parser.add_argument(
            '--restore-media',
            action='store_true',
            help='Restaurar arquivos de mídia'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forçar restauração sem confirmação'
        )

    def handle(self, *args, **options):
        backup_file = options['backup_file']
        restore_media = options['restore_media']
        force = options['force']
        
        if not os.path.exists(backup_file):
            self.stdout.write(
                self.style.ERROR(f'Arquivo de backup não encontrado: {backup_file}')
            )
            return
        
        # Confirmação do usuário
        if not force:
            confirm = input(
                'ATENÇÃO: Esta operação irá substituir todos os dados atuais. '
                'Tem certeza que deseja continuar? (digite "SIM" para confirmar): '
            )
            if confirm != 'SIM':
                self.stdout.write('Operação cancelada.')
                return
        
        # Verificar se é arquivo ZIP
        if backup_file.endswith('.zip'):
            self.restore_from_zip(backup_file, restore_media)
        else:
            self.restore_from_json(backup_file)
        
        self.stdout.write(
            self.style.SUCCESS('Restauração concluída com sucesso!')
        )

    def restore_from_zip(self, zip_file, restore_media):
        """Restaura backup de arquivo ZIP"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(zip_file, 'r') as zipf:
                zipf.extractall(temp_dir)
            
            # Encontrar arquivo JSON do banco
            json_files = [f for f in os.listdir(temp_dir) if f.endswith('.json')]
            if json_files:
                json_file = os.path.join(temp_dir, json_files[0])
                self.restore_database(json_file)
            
            # Restaurar arquivos de mídia
            if restore_media:
                media_dir = os.path.join(temp_dir, 'media')
                if os.path.exists(media_dir):
                    self.restore_media_files(media_dir)

    def restore_from_json(self, json_file):
        """Restaura backup de arquivo JSON"""
        self.restore_database(json_file)

    def restore_database(self, json_file):
        """Restaura banco de dados"""
        self.stdout.write('Restaurando banco de dados...')
        
        # Fazer backup do banco atual antes de restaurar
        backup_file = f'backup_before_restore_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(backup_file, 'w') as f:
            call_command('dumpdata', stdout=f, indent=2)
        
        self.stdout.write(f'Backup de segurança criado: {backup_file}')
        
        # Limpar banco atual
        call_command('flush', '--noinput')
        
        # Restaurar dados
        with open(json_file, 'r') as f:
            call_command('loaddata', json_file)
        
        self.stdout.write('Banco de dados restaurado com sucesso!')

    def restore_media_files(self, media_dir):
        """Restaura arquivos de mídia"""
        if not hasattr(settings, 'MEDIA_ROOT'):
            self.stdout.write(
                self.style.WARNING('MEDIA_ROOT não configurado, pulando restauração de mídia')
            )
            return
        
        self.stdout.write('Restaurando arquivos de mídia...')
        
        # Criar diretório de mídia se não existir
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        
        # Copiar arquivos
        import shutil
        for root, dirs, files in os.walk(media_dir):
            for file in files:
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, media_dir)
                dst_path = os.path.join(settings.MEDIA_ROOT, rel_path)
                
                # Criar diretório de destino se necessário
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                
                # Copiar arquivo
                shutil.copy2(src_path, dst_path)
        
        self.stdout.write('Arquivos de mídia restaurados com sucesso!')
