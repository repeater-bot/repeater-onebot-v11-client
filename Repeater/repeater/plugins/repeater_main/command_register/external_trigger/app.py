from fastapi import FastAPI

et_app = FastAPI(
    title="Repeater External Trigger",
    description = "A task is submitted outside the Repeater via HTTP and the output is submitted to a Bot instance.",
    version = "0.0.1"
)