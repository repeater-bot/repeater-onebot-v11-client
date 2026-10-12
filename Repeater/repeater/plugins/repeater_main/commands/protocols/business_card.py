import json
from datetime import datetime

from ...assist import PersonaInfo, SendMsg, BusinessCard as PersonaBusinessCard, GroupMemberInfo
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)

@CommandCaller.register
class BusinessCard(CommandPackage):
    cmd = "businessCard"
    aliases = {
        "bc",
        "BC",
        "business_card",
        "Business_Card"
        "BusinessCard",
        "BUSINESS_CARD"
    }
    cmd_type = CmdTypes.PROTOCOL
    description = f"""
    Gets the business card of the specified person.
    If not, generate your own.

    Usage: 
    ```
    /{cmd} @member
    ```
    """
    def gen_business_card(self, persona_business_card: PersonaBusinessCard, group_member_info: GroupMemberInfo | None = None) -> str:
        text_buffer: list[str] = []
        if group_member_info is not None:
            if group_member_info.card:
                text_buffer.append(f"# {json.dumps(group_member_info.card, ensure_ascii=False)}")
            else:
                text_buffer.append(f"# {json.dumps(group_member_info.nickname, ensure_ascii=False)}")
        else:
            text_buffer.append(f"# {json.dumps(persona_business_card.nickname, ensure_ascii=False)}")

        text_buffer.append(f"**Name: **{json.dumps(persona_business_card.nickname, ensure_ascii=False)}")
        if group_member_info is not None:
            if group_member_info.card:
                text_buffer.append(f"**Group Nickname: **{json.dumps(group_member_info.card, ensure_ascii=False)}")
        text_buffer.append(f"**QQ: **{json.dumps(persona_business_card.user_id, ensure_ascii=False)}")
        text_buffer.append(f"**Gender: **{json.dumps(persona_business_card.sex, ensure_ascii=False)}")
        text_buffer.append(f"**Age: **{json.dumps(persona_business_card.age, ensure_ascii=False)}")
        if group_member_info is not None:
            text_buffer.append(f"**Is Robot: **{json.dumps(group_member_info.is_robot, ensure_ascii=False)}")
        text_buffer.append(f"**Personal signature: **{json.dumps(persona_business_card.long_nick, ensure_ascii=False)}")
        text_buffer.append(f"**QQ level: **{json.dumps(persona_business_card.qq_level, ensure_ascii=False)}")
        if group_member_info is not None:
            text_buffer.append(f"**Group Level: **{json.dumps(group_member_info.level, ensure_ascii=False)}")
        text_buffer.append("**QQVIP:**")
        text_buffer.append(f"- **is_vip: **{json.dumps(persona_business_card.is_vip, ensure_ascii=False)}")
        text_buffer.append(f"- **is_years_vip: **{json.dumps(persona_business_card.is_years_vip, ensure_ascii=False)}")
        text_buffer.append(f"- **vip_level: **{json.dumps(persona_business_card.vip_level, ensure_ascii=False)}")
        if group_member_info is not None:
            text_buffer.append(f"**Join group time: **{json.dumps(datetime.fromtimestamp(group_member_info.join_time).isoformat(), ensure_ascii=False)}")
            text_buffer.append(f"**Last speak time: **{json.dumps(datetime.fromtimestamp(group_member_info.last_sent_time).isoformat(), ensure_ascii=False)}")
        return "\n".join(text_buffer)
        

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        at_list = persona_info.at_list
        if not at_list:
            persona_list = [persona_info.user_id]
        else:
            persona_list = at_list

        text_buffer: list[str] = []
        for user_id in persona_list:
            persona_business_card = await persona_info.get_stranger_info(
                user_id = user_id
            )

            if persona_info.is_group and persona_info.group_id is not None:
                group_member_info = await persona_info.get_group_member_info(
                    group_id = persona_info.group_id,
                    user_id = user_id
                )
            else:
                group_member_info = None
            
            text = self.gen_business_card(
                persona_business_card,
                group_member_info
            )
            text_buffer.append(text)

        await send_msg.send_render("\n\n---\n\n".join(text_buffer))
            