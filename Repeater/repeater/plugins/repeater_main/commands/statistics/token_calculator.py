import time
import asyncio
from ...assist import PersonaInfo, FileInfo, SendMsg, Downloader
from ...cmd_info import CmdTypes
from ...command_register import(
    CommandCaller,
    CommandPackage
)
from tokenizers import Encoding, Tokenizer
from collections import Counter
from ...logger import logger
from cachetools import LRUCache
from ...client_configs import storage_configs

@CommandCaller.register
class TokenCalculator(CommandPackage):
    cmd = "tokenizer"
    aliases = {
        "tiz",
        "TIZ",
        "Tokenizer",
        "TOKENIZER"
    }
    cmd_type = CmdTypes.STATISTIC
    description = f"""
    Count tokens using tokenizer.

    Usage:
    (reply a tokenizer file)
    ```
    /{cmd} text
    ```
    """
    cache_lock = asyncio.Lock()
    cache: LRUCache[FileInfo, Tokenizer] = LRUCache(maxsize=storage_configs.tokenizer_cache_size)

    def __init__(self):
        self.downloader = Downloader(usage_global_client = True)
    
    def init_tokenizer(self, file_info: FileInfo, content: bytes) -> Tokenizer:
        if file_info in self.cache:
            tokenizer = self.cache[file_info]
        else:
            tokenizer = Tokenizer.from_buffer(content)
            self.cache[file_info] = tokenizer
        return tokenizer

    async def get_files(self, persona_info: PersonaInfo) -> list[FileInfo]:
        file_ids: list[FileInfo] = []
        for msg in await persona_info.from_reversed_reply_chain():
            file_ids.extend(msg.get_file_infos())
        file_ids.extend(persona_info.get_file_infos())
        return file_ids

    async def get_file_content(self, file_info: FileInfo) -> bytes:
            file_content = await self.downloader.download_file(
                url = file_info.url
            )
            return file_content

    async def handler(self, persona_info: PersonaInfo, send_msg: SendMsg):
        file_infos = await self.get_files(persona_info)
        if not file_infos:
            await send_msg.send_error("Need a tokenizer.json for reference.")
            send_msg.break_handler()
        elif len(file_infos) > 1:
            await send_msg.send_error("Only one tokenizer.json is allowed.")
            send_msg.break_handler()
        else:
            file_content = await self.get_file_content(file_infos[0])
            
        logger.info("Loading tokenizer...")
        init_start_time = time.perf_counter_ns()
        async with self.cache_lock:
            tokenizer = await asyncio.to_thread(
                self.init_tokenizer,
                file_info = file_infos[0],
                content = file_content
            )
        init_end_time = time.perf_counter_ns()
        logger.info("Inited tokenizer in {init_time:.2f}ms.", init_time=(init_end_time - init_start_time) / 1e6)
        logger.info("Calculating tokens...")
        start_time = time.perf_counter_ns()
        tokens_encoding: Encoding = await asyncio.to_thread(
            tokenizer.encode,
            persona_info.message_stripped_str
        )
        end_time = time.perf_counter_ns()
        logger.info("Calculated tokens in {calc_time:.2f}ms.", calc_time=(end_time - start_time) / 1e6)
        tokens_count = len(tokens_encoding.ids)
        text_count = len(persona_info.message_stripped_str)
        most_frequent = await asyncio.to_thread(
            self.make_most_frequent,
            tokenizer,
            tokens_encoding
        )

        await self.output(
            send_msg = send_msg,
            tokens_count = tokens_count,
            text_count = text_count,
            most_frequent = most_frequent
        )

    def make_most_frequent(self, tokenizer: Tokenizer, encoding: Encoding) -> list[str]:
        counter = Counter(encoding.ids)
        most_frequent: list[str] = ["Most frequent:"]
        for id, count in counter.most_common(storage_configs.tokenizer_most_frequent_tokens):
            token = tokenizer.id_to_token(id) or "[UNK]"
            token_text = f"[{id}|{count}]: 0x{token.encode('utf-8').hex()}"
            most_frequent.append(token_text)

        return most_frequent

    async def output(
            self,
            send_msg: SendMsg,
            tokens_count: int,
            text_count: int,
            most_frequent: list[str]
        ):
        await send_msg.send_mixed_render(
            prefix_text = "\n".join(
                [
                    f"Token count: {tokens_count}",
                    f"Text length: {text_count}",
                    f"Average something conversion rate: {tokens_count / text_count:.2%}(1:{tokens_count / text_count:.2f})"
                ]
            ),
            text_to_render = "  - " + "\n  - ".join(most_frequent)
        )