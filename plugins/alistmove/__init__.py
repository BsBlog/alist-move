import subprocess
from app.core.config import settings
from app.core.event import eventmanager, Event
from app.plugins import _PluginBase
from app.log import logger
from app.schemas import TransferInfo
from app.schemas.types import EventType
from app.utils.http import RequestUtils

class AlistMove(_PluginBase):
    # 插件名称
    plugin_name = "Alist Move"
    # 插件描述
    plugin_desc = "整理完成后自动Alist Move"
    # 插件图标
    plugin_icon = "Alist_B.png"
    # 插件版本
    plugin_version = "1.0.0"
    # 插件作者
    plugin_author = "None"
    # 作者主页
    author_url = "None"
    # 插件配置项ID前缀
    plugin_config_prefix = "Alist_Move_"
    # 加载顺序
    plugin_order = 1
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _enabled = False
    _onlyonce = False

    def init_plugin(self, config: dict = None):
        # 读取配置
        if config:
            self._enabled = config.get("enabled")
            self._onlyonce = config.get("onlyonce")
            self._GH_Token = config.get("GH_Token")

        # 停止现有任务
        self.stop_service()

        # 立即运行一次
        if self._onlyonce:
            logger.info(f"立即运行一次")
            # 关闭一次性开关
            self._onlyonce = False
            self.update_config({
                "onlyonce": False,
                "enabled": self._enabled,
            })
        if self._scheduler.get_jobs():
            # 启动服务
            self._scheduler.print_jobs()
            self._scheduler.start()

    def get_state(self) -> bool:
        return self._enabled

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        pass

    def get_api(self) -> List[Dict[str, Any]]:
        pass

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        return [
            {
                'component': 'VForm',
                'content': [
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VSwitch',
                                        'props': {
                                            'model': 'enabled',
                                            'label': '启用插件',
                                        }
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'component': 'VCol',
                        'props': {
                            'cols': 12,
                            'md': 6
                        },
                        'content': [
                            {
                                'component': 'VSwitch',
                                'props': {
                                    'model': 'onlyonce',
                                    'label': '立即运行一次',
                                }
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {
                                    'cols': 12,
                                    'md': 6
                                },
                                'content': [
                                    {
                                        'component': 'VTextField',
                                        'props': {
                                            'model': 'GH_Token',
                                            'label': 'Github API 密钥'
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ], {
            "enabled": False,
            "GH_Token": "",
        }

    @eventmanager.register(EventType.TransferComplete)
    def Alist_Move(self, event: Event):
        curl_command = [
            "curl",
            "--location",
            "https://api.github.com/repos/BsBlog/alist-move/dispatches",
            "--header", "Authorization: token " + self._GH_Token,
            "--header", "Content-Type: application/json",
            "--data", '{"event_type": "Alist-Move"}'
        ]

        try:
            subprocess.run(curl_command, check=True)
            logger.info("GitHub dispatch event triggered successfully.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to trigger GitHub dispatch event: {e}")