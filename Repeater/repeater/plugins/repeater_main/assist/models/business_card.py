from pydantic import BaseModel, Field, ConfigDict

class CustomStatus(BaseModel):
    model_config = ConfigDict(
        extra = "allow"
    )
    
    faceId: int = 0
    wording: str = ""

class BusinessCard(BaseModel):
    model_config = ConfigDict(
        extra = "allow"
    )

    user_id: int = 0
    uid: str = ""
    qid: str = ""
    nickname: str = ""
    remark: str = ""
    sex: str = ""
    age: int = 0
    long_nick: str = ""
    qq_level: int = 0
    qqLevel: int = 0
    level: int = 0
    reg_time: int = 0
    is_vip: bool = False
    is_years_vip: bool = False
    vip_level: int = 0
    status: int = 0
    extStatus: int = 0
    ext_status: int = 0
    batteryStatus: int = 0
    customStatus: CustomStatus | None = None
    customStatusDescInfo: str = ""
    qidian_master_flag: int = 0
    qidian_crew_flag: int = 0
    qidian_crew_flag_2: int = 0
    qidian_enterprise_name: str = ""