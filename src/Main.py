import os
from vkbottle.bot import Bot, Message
from vkbottle import API
from datetime import datetime
import random
from enums.Metrics import Metric
from enums.questions import Question
from models.response import Response

API_TOKEN_USER = os.environ.get('API_TOKEN_USER')
API_TOKEN_BOT = os.environ.get('API_TOKEN_BOT')
domain = os.environ.get('domain')

api = API(token=API_TOKEN_USER)
bot = Bot(token=API_TOKEN_BOT)

current_users_requests = dict()
users_response = dict()


def getTime(time):
    return str(datetime.utcfromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S'))


def castTime(text):
    return datetime.strptime(text, '%d.%m.%Y')


async def getStatistic(response) -> str:
    data = (await api.wall.get(domain=domain, count=response.CountPosts)).items
    data = [x for x in data if not response.TimeFilterNeeded or
            response.DateTimeStart <= datetime.fromtimestamp(x.date) <= response.DateTimeEnd]
    metrics_values = [post.__getattribute__(response.Metric).count for post in data]
    response.MetricValue = metrics_values
    dm = 0
    for i in range(1, len(metrics_values)):
        dm += metrics_values[i - 1] - metrics_values[i]
    if len(metrics_values) <= 1:
        dm = 0
    else:
        dm /= len(metrics_values) - 1
    response.Increment = dm
    response.IsDone = True
    return f"Всего постов в выборке: {len(data)}\n{response.Metric}: {metrics_values}\nПрирост (убыток): {dm}"


@bot.on.message(text=[Metric.Views.value, Metric.Likes.value,
                      Metric.Reposts.value, Metric.Comments.value])
async def messages_metrics_handler(message: Message) -> str:
    resp = Response(random.randint(1, 1000000), message.from_id,
                    message.text, None, None, None, None,
                    None, None, None)
    users_response[message.from_id] = resp
    return Question.PostCount.value


@bot.on.message()
async def message_other_type_handler(message: Message) -> str:
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
        try:
            resp.DateTimeStart = castTime(message.text)
        except:
            return Question.Error.value
        return Question.PostTimeEnd.value
    if resp.DateTimeEnd is None and resp.TimeFilterNeeded:
        try:
            resp.DateTimeEnd = castTime(message.text)
        except:
            return Question.Error.value
        return await getStatistic(resp)
    return Question.Error.value


if __name__ == "__main__":
    bot.run_forever()
