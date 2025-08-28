import asyncio
from src.infrastructure.integrations.whatsapp.whatsapp_config import WhatsAppClient

async def test_send():
    client = WhatsAppClient()
    
    # Replace with your test number
    test_number = "17037276762"
    
    result = await client.send_message(
        test_number,
        "¡Hola! Este es un mensaje de prueba desde RepuAI."
    )
    
    print(f"Message sent: {result}")

if __name__ == "__main__":
    asyncio.run(test_send())