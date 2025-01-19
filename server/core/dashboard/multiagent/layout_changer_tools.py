import sys

sys.path.append("")

from langchain_core.tools import tool

@tool
async def login(*args) -> str:
    """"Use this when user wants to login. This tool adjusts the frontend so that the user could input his email and password."""
    return "Login tool executed."

@tool
async def signup_email(*args) -> str:
    """"Use this when user wants to sign up. This tool adjusts the frontend so that the user could input his email, after which a confirmation email will be sent."""
    return "Signup tool executed."

@tool
async def forgot_password(*args) -> str:
    """"Use this when user forgot password or wants to reset password. This tool adjusts the frontend so that the user could input his email, after which a confirmation email with password reset link will be sent."""
    return "Forgot Password tool executed."

layout_changer_tools = [
    login,
    signup_email,
    forgot_password,
]

layout_changer_toolnames = [tool.name for tool in layout_changer_tools]

if __name__ == "__main__":
    print(layout_changer_toolnames)