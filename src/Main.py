from vkbottle.bot import Bot, Message
from vkbottle import API
from datetime import datetime
import secrets

api = API(token=secrets.API_TOKEN_USER)
bot = Bot(token=secrets.API_TOKEN_BOT)

users_epoch = dict()
current_users_requests = dict()
users_response = dict()


def getTime(time):
    return str(datetime.utcfromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S'))


@bot.on.message(text="стат")
async def messages_handler(message: Message) -> str:
    response = await api.wall.get(domain=secrets.domain, count=10, filter="owner")
    answer = ""
    for post in response.items:
        answer += f"Дата поста: {getTime(post.date)}\n"
        answer += f"Количество лайков под постом: {post.likes.count}\n\n"
    answer += f"\nВсего обработано постов: {len(response.items)}"
    return answer


bot.run_forever()
