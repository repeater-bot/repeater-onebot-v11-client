from pydantic import BaseModel


class GroupMemberInfo(BaseModel):
    group_id: int = 0
    user_id: int = 0
    nickname: str = ""
    card: str = ""
    is_robot: bool = False
    sex: str = ""
    age: int = 0
    join_time: int = 0
    last_sent_time: int = 0
    shut_up_timestamp: int = 0
    level: int = 0
    qq_level: int = 0
    qage: int = 0
    role: str = ""
    title: str = ""
    area: str = ""
    unfriendly: bool = False
    title_expire_time: int = 0
    card_changeable: bool = False
    qidian_master_flag: bool = False
    qidian_crew_flag: bool = False
    qidian_crew_flag_2: bool = False