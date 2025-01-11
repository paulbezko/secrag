import json
from typing import List, Literal

from pydantic import BaseModel, Field

from custom_langgraph_methods import create_react_agent_with_node_name
from globals import State
from helpers import get_last_message
import os

import base64
from PIL import Image
from io import BytesIO

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.types import Command
from langchain_core.messages import AIMessage, HumanMessage



class PortfolioItem(BaseModel):
    asset: str = Field("Name or symbol of the asset (e.g., GOOGL, MU).")
    price: float | None = Field("Current price of the asset.")
    units: float | None = Field("Number of units owned.")
    pl: float | None = Field("Profit or Loss for the asset.")
    value: float | None = Field("Total value of the asset in the portfolio.")

class Portfolio(BaseModel):
    success: bool = Field("Reading portfolio was successful")
    items: List[PortfolioItem] | None = Field("List of portfolio items.")
    comments: str = Field("Comments about the portfolio extraction.")

portfolio_reader_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", """Your task is to extract user investment Portfolio data from images.\
                  If the image does not contain any portfolio data, \
                 respond with "No portfolio data found"."""),
                MessagesPlaceholder("messages")
            ]
)

llm_portfolio_reader = ChatOpenAI(model="gpt-4o-mini").with_structured_output(Portfolio)
portfolio_reader_chain = portfolio_reader_prompt | llm_portfolio_reader

async def portfolio_reader_node(state: State) -> Command[Literal["__end__"]]:
    result = await portfolio_reader_chain.ainvoke({"messages": [get_last_message(state["messages"], "user"), get_last_message(state["messages"], "ai")]})
    return Command(
        graph="portfolio_reader",
        update={
            "messages": [
                AIMessage(
                    content=result["messages"][-1].content, name="portfolio_reader"
                )
            ]
        },
        goto="__end__"
    )

def encode_image_to_jpeg_base64(image_path):
    try:
        # Open the image
        with Image.open(image_path) as img:
            # Calculate resizing to ensure max 2.073 million pixels
            max_pixels = 2073600  # Maximum allowed pixels
            width, height = img.size
            total_pixels = width * height
            
            if total_pixels > max_pixels:
                scale_factor = (max_pixels / total_pixels) ** 0.5
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                img = img.resize((new_width, new_height), Image.ANTIALIAS)
            
            # Convert to JPEG format
            buffer = BytesIO()
            img.convert("RGB").save(buffer, format="JPEG")
            
            # Encode to Base64
            base64_string = base64.b64encode(buffer.getvalue()).decode("utf-8")
            
            return base64_string
    except Exception as e:
        print(f"Error encoding image: {e}")
        raise e


def create_human_message_with_image(images: list, text: str = ""):
    message = HumanMessage(
        content=[
            {"type": "text", "text": text},
            
        ],
    )
    for image_data in images:
        message.content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}},)
    return message


if __name__ == "__main__":
    path = "portfolio_reader_test_images"
    images = os.listdir(path)
    encoded_images = []
    for image in images:
        print(image)
        image_path = os.path.join(path, image)
        base64_string = encode_image_to_jpeg_base64(image_path)
        encoded_images.append(base64_string)
    
    message = create_human_message_with_image(encoded_images)
    
    result = portfolio_reader_chain.invoke({"messages":[message]})

    print(result)
    print(json.dumps(result.model_dump(), indent=2))

