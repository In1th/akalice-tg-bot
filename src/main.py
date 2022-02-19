import asyncio
from exceptions import *
import setup
import datetime
import time
from settings import *

async def main():
    start_time = time.time()


    properties_task = asyncio.create_task(setup.load_properties("properties.json"))
    
    print(TITTLE)
    print("---------------------------------")
    print(f"Wersja v{VERSION_NO} ({VERSION_DATE})")
    print("---------------------------------")

    properties = await properties_task
    properties_dict = properties

    updater, dispatcher = setup.init_api_con(properties["API_KEY"])
    await setup.load_handlers(dispatcher)
    
    print(f"{datetime.datetime.now()} 》Konfiguracja zakończona! (czas = {time.time() - start_time}s)")
    updater.start_polling()
    updater.idle()
    print(f"{datetime.datetime.now()} 》Program zakończył się!")

if __name__ == "__main__":
    asyncio.run(main())
