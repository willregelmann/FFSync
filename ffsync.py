import yaml, os, sys, shutil, _winapi, subprocess

def tell(str): print("\033[95mFF Sync >> %s\033[0m"%(str))
def get_reply(): return input("\033[95m>> FF: \033[0m")
def emote(str): print("\033[96mFF Sync %s\033[0m"%(str))

tell('o/')

config = yaml.load(open('conf.yaml'), Loader=yaml.Loader)
if 'backupLocation' not in config:
    tell('Please specify a backupLocation in conf.yaml')
    sys.exit()

if not os.path.exists(config['backupLocation']): 
    os.mkdir(config['backupLocation'])
    emote('synthesizes %s'%(config['backupLocation']))

local_dir = '%s\Documents\My Games\Final Fantasy XIV - A Realm Reborn'%(os.getenv('USERPROFILE'))
local_char_dirs = filter(lambda dir: dir.startswith('FFXIV_CHR'), next(os.walk(local_dir))[1])
backup_dir = config['backupLocation']
backup_char_dirs = filter(lambda dir: dir.startswith('FFXIV_CHR'), next(os.walk(backup_dir))[1])
backup_shared_dir = '%s\FFXIV_SHARED'%(backup_dir)

if 'characterSync' in config and not os.path.exists(backup_shared_dir): 
    os.mkdir(backup_shared_dir)
    emote('synthesizes %s'%(backup_shared_dir))

while True:
    tell('In case of conflicts, should I keep (1) the local settings, or (2) the backup settings?')
    tiebreaker = get_reply()
    if tiebreaker in ['1', '2']: break
    tell('Please enter 1 or 2')

most_recent_login = 0
most_recent_dir = None

# back local settings up
for dir in local_char_dirs:
    local_path = '%s\%s'%(local_dir, dir)
    backup_path = '%s\%s'%(backup_dir, dir)
    for log_file in os.listdir('%s\log'%(local_path)):
        if os.path.getmtime('%s\log\%s'%(local_path, log_file)) > most_recent_login:
            most_recent_login = os.path.getmtime('%s\log\%s'%(local_path, log_file))
            most_recent_dir = dir
    if os.path.islink(local_path): continue
    if dir in backup_char_dirs:
        if tiebreaker == '1': 
            if os.path.exists('%s_BAK'%(backup_path)): shutil.rmtree('%s_BAK'%(backup_path))
            os.rename(backup_path, '%s_BAK'%(backup_path))
        if tiebreaker == '2': continue
    shutil.move(local_path, backup_dir)
    emote('moves %s to %s'%(local_path, backup_dir))
    
# prepare synced character settings
if 'characterSync' in config:
    if not os.path.exists('%s\FFXIV_SHARED'%(local_dir)): 
        _winapi.CreateJunction(backup_shared_dir, '%s\FFXIV_SHARED'%(local_dir))
    for file in config['characterSync']:
        backup_path = '%s\%s.DAT'%(backup_shared_dir, file)
        if os.path.exists(backup_path):
            if tiebreaker == '1': 
                if os.path.exists('%s.BAK'%(backup_path)): 
                    os.chmod('%s.BAK'%(backup_path), 0o777)
                    os.remove('%s.BAK'%(backup_path))
                os.rename(backup_path, '%s.BAK'%(backup_path))
            elif tiebreaker == '2': continue
        shutil.move('%s\%s\%s.DAT'%(backup_dir, dir, file), backup_path)

# sync backup settings with local
for dir in filter(lambda dir: dir.startswith('FFXIV_CHR'), next(os.walk(backup_dir))[1]):
    local_path = '%s\%s'%(local_dir, dir)
    backup_path = '%s\%s'%(backup_dir, dir)
    if os.path.exists(local_path):
        if os.path.islink(local_path): continue
        if os.path.exists('%s_BAK'%(local_path)): shutil.rmtree('%s_BAK'%(local_path))
        os.rename(local_path, '%s_BAK'%(local_path))
    _winapi.CreateJunction(backup_path, local_path)
    if 'characterSync' in config:
        for file in config['characterSync']:
            file_path = '%s\%s.DAT'%(local_path, file)
            shared_file_path = '%s\FFXIV_SHARED\%s.DAT'%(local_dir, file)
            if os.path.exists(file_path):
                if os.path.islink(file_path): continue
                if os.path.exists('%s.BAK'%(file_path)): 
                    os.chmod('%s.BAK'%(file_path), 0o777)
                    os.remove('%s.BAK'%(file_path))
                os.rename(file_path, '%s.BAK'%(file_path))
            os.symlink(shared_file_path, file_path)
            
tell('tyfp!')