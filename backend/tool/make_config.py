import configparser
import os


def make_config():
    config = configparser.ConfigParser()
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(script_dir, 'config.ini')
    config.read(config_file_path)
    return {
            "supabase": {
                "command": config.get('supabase', 'command'),
                "args": config.get('supabase', 'args').split(','),
                "transport": config.get('supabase', 'transport'),
            },
            # "redis": {
            #     "command": config.get('redis', 'command'),
            #     "args": config.get('redis', 'args').split(','),
            #     "env": {
            #         "REDIS_HOST": config.get('redis', 'env_redis_host'),
            #         "REDIS_PORT": config.get('redis', 'env_redis_port')
            #     },
            #     "transport": config.get('redis', 'transport')
            # },
        }