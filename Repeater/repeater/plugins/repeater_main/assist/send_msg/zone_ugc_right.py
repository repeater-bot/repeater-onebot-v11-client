from enum import StrEnum

class ZoneUGCRight(StrEnum):
    """
    QQ Zone UGC 权限
    """
    ALL = "all"
    FRIEND = "friend"
    ONLY_CERTAIN_FRIEND = "only_certain_friend"
    EXCLUDE_CERTAIN_FRIEND = "exclude_certain_friend"
    ONLY_SELF = "only_self"

    def to_zone_ugc_right_num(self) -> int:
        match self:
            case ZoneUGCRight.ALL:
                return 1
            case ZoneUGCRight.FRIEND:
                return 4
            case ZoneUGCRight.ONLY_CERTAIN_FRIEND:
                return 16
            case ZoneUGCRight.EXCLUDE_CERTAIN_FRIEND:
                return 64
            case ZoneUGCRight.ONLY_SELF:
                return 128
        
        raise ValueError("Invalid ZoneUGCRight")