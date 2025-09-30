from chalice import Chalice
from chalicelib.venues import ComedyCellarBot, TheStandBot
from chalicelib.email_service import EmailService
from chalicelib.bot_service import ComedyBotService
from chalicelib.config import Config

app = Chalice(app_name="comedy-show-bots", debug=True)

email_service = EmailService(region_name=Config.AWS_REGION)
venues = [ComedyCellarBot(), TheStandBot()]
bot_service = ComedyBotService(venues=venues, email_service=email_service)


@app.schedule("cron(0 13 * * ? *)")  # 13:00 UTC = 9 AM EDT / 8 AM EST
def check_comedy_shows(event):
    print(f"Event: {event.to_dict()}")

    try:
        results = bot_service.check_all_venues()
        bot_service.send_comedy_alerts(results)
        print("Comedy show check completed successfully")
    except Exception as e:
        print(f"Error in comedy show check: {e}")
        raise
