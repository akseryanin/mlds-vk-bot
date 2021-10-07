from vkbottle.bot import Bot, Message
from vkbottle import API
from datetime import datetime
import random
import secrets
import time
from enums.Metrics import Metric
from enums.questions import Question
from models.response import Response

api = API(token=secrets.API_TOKEN_USER)
bot = Bot(token=secrets.API_TOKEN_BOT)

current_users_requests = dict()
users_response = dict()


def getTime(time):
    return str(datetime.utcfromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S'))

def castTime(text):
    d = datetime.strptime(text, '%d %m %Y')
    return d


async def getStatistic(response) -> str:
    data = (await api.wall.get(domain=secrets.domain, count=response.CountPosts)).items
    data = [x for x in data if not response.TimeFilterNeeded or
            response.DateTimeStart <= datetime.fromtimestamp(x.date) <= response.DateTimeEnd]
    metrics_values = [post.__getattribute__(response.Metric).count for post in data]
    response.MetricValue = metrics_values
    dm = 0
    for i in range(1, len(metrics_values)):
        dm += metrics_values[i - 1] - metrics_values[i]
    dm /= len(metrics_values) - 1
    response.Increment = dm
    response.IsDone = True
    return f"Всего постов в выборке: {len(data)}\n{response.Metric}: {metrics_values}\nПрирост (убыток): {dm}"


@bot.on.message(text="стат")
async def messages_handler(message: Message) -> str:
    response = await api.wall.get(domain=secrets.domain, count=10)
    answer = ""
    for post in response.items:
        answer += f"Дата поста: {getTime(post.date)}\n"
        answer += f"Количество лайков под постом: {post.likes.count}\n\n"
    answer += f"\nВсего обработано постов: {len(response.items)}"
    return answer


@bot.on.message(text=["likes", "reposts", "comments"])
async def messages_metrics_handler(message: Message) -> str:
    resp = Response(random.randint(1, 1000000), message.from_id,
                    message.text, None, None, None, None,
                    None, None, None)
    resp.UserId = message.from_id
    resp.Metric = message.text
    users_response[message.from_id] = resp
    return Question.PostCount.value


@bot.on.message()
async def message_other_type(message: Message) -> str:

    resp = users_response[message.from_id]
    if resp.CountPosts is None:
        try:
            resp.CountPosts = int(message.text)
        except:
            return str(Question.Error)
        return Question.PostTimeRange.value
    if resp.TimeFilterNeeded is None:
        resp.TimeFilterNeeded = message.text == "+"
        if resp.TimeFilterNeeded:
            return Question.PostTimeBegin.value
        return await getStatistic(resp)
    if resp.DateTimeStart is None and resp.TimeFilterNeeded:
        resp.DateTimeStart = castTime(message.text)
        return Question.PostTimeEnd.value
    if resp.DateTimeEnd is None and resp.TimeFilterNeeded:
        resp.DateTimeEnd = castTime(message.text)
        return await getStatistic(resp)


if __name__ == "__main__":
    bot.run_forever()
