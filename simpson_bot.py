import tweepy
import datetime
import json
import urllib.request
import time
import random

def get_api(cfg):
  auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
  auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
  return tweepy.API(auth)

def time_converter(time):
    converted_time = datetime.datetime.fromtimestamp(
        int(time)
    ).strftime('%I:%M %p')
    return converted_time


def url_builder(city_id):
    user_api = ''  # Obtain yours form: http://openweathermap.org/
    unit = 'metric'  # For Fahrenheit use imperial, for Celsius use metric, and the default is Kelvin.
    api = 'http://api.openweathermap.org/data/2.5/weather?id='     # Search for your city ID here: http://bulk.openweathermap.org/sample/city.list.json.gz

    full_api_url = api + str(city_id) + '&mode=json&units=' + unit + '&APPID=' + user_api
    return full_api_url


def data_fetch(full_api_url):
    url = urllib.request.urlopen(full_api_url)
    output = url.read().decode('utf-8')
    raw_api_dict = json.loads(output)
    url.close()
    return raw_api_dict


def data_organizer(raw_api_dict):
    data = dict(
        city=raw_api_dict.get('name'),
        country=raw_api_dict.get('sys').get('country'),
        temp=raw_api_dict.get('main').get('temp'),
        temp_max=raw_api_dict.get('main').get('temp_max'),
        temp_min=raw_api_dict.get('main').get('temp_min'),
        humidity=raw_api_dict.get('main').get('humidity'),
        pressure=raw_api_dict.get('main').get('pressure'),
        sky=raw_api_dict['weather'][0]['main'],
        sunrise=time_converter(raw_api_dict.get('sys').get('sunrise')),
        sunset=time_converter(raw_api_dict.get('sys').get('sunset')),
        wind=raw_api_dict.get('wind').get('speed'),
        wind_deg=raw_api_dict.get('deg'),
        dt=time_converter(raw_api_dict.get('dt')),
        cloudiness=raw_api_dict.get('clouds').get('all')
    )
    return data


def data_output(data):
    # m_symbol = '\xb0' + 'C'
    # print('---------------------------------------')
    # print('Current weather in: {}, {}:'.format(data['city'], data['country']))
    # print(data['temp'], m_symbol, data['sky'])
    # print('Max: {}, Min: {}'.format(data['temp_max'], data['temp_min']))
    # print('')
    # print('Wind Speed: {}, Degree: {}'.format(data['wind'], data['wind_deg']))
    # print('Humidity: {}'.format(data['humidity']))
    # print('Cloud: {}'.format(data['cloudiness']))
    # print('Pressure: {}'.format(data['pressure']))
    # print('Sunrise at: {}'.format(data['sunrise']))
    # print('Sunset at: {}'.format(data['sunset']))
    # print('')
    # print('Last update from the server: {}'.format(data['dt']))
    # print('---------------------------------------')
    return data

class MarkovChain:

    def __init__(self, n=2):
        self.n = n
        self.memory = {}

    def _learn_key(self, key, value):
        if key not in self.memory:
            self.memory[key] = []

        self.memory[key].append(value)

    def learn(self, text):
        tokens = [token.strip('()') for token in text.split(" ")]
        if self.n==2:
            ngrams = [(tokens[i], tokens[i+1]) for i in range(0, len(tokens) - 1)]
        else:
            # n==3
            ngrams = [(tokens[i], tokens[i+1], tokens[i+2]) for i in range(0, len(tokens) - 2)]
        for ngram in ngrams:
            if self.n==2:
                self._learn_key(ngram[0], ngram[1])
            else:
                self._learn_key((ngram[0], ngram[1]), ngram[2])

    def _next(self, current_state):
        next_possible = self.memory.get(current_state)

        if not next_possible:
            if self.n==2:
                next_possible = self.memory.keys()
            else:
                next_possible = [key[0] for key in self.memory.keys()]

        return random.sample(next_possible, 1)[0]

    def babble(self, amount, state=''):
        if not amount:
            return state

        next_word = self._next(state)
        return state + ' ' + self.babble(amount - 1, next_word)


def compose_tweet(model, prompt):
    tweet = model._next(prompt).capitalize()
    next_word = model._next(tweet)
    while len(tweet) < 100 or len(tweet + next_word) <= 215:
        tweet += ' ' + next_word
        next_word = model._next(next_word)
        if len(tweet) > 150 and tweet[-1] in ['.', '!', '?']:
            break
    return tweet

def main():
  # Twitter keys
  cfg = {
      "consumer_key"        : "",
      "consumer_secret"     : "",
      "access_token"        : "",
       "access_token_secret": ""
  }

  api = get_api(cfg)
  city_id = 4525353 #Springfield USA
  txt_file = open('Homer_Weather/data/cleaned.txt')
  txt = txt_file.read().replace('\n', ' ')

  markov = MarkovChain(2)
  markov.learn(txt)

  try:

      weather_info = data_output(data_organizer(data_fetch(url_builder(city_id))))

      if(weather_info['sky'] in ['Rain', 'Extreme', 'Snow','Thunderstorm']):
            prompt = 'Whew!'
      else:
            prompt = ''

      tweet = 'Today in Springfield it\'s {} with an average of {} {}. '.format(weather_info['sky'].lower(), round(weather_info['temp']),'\xb0' + 'C')+compose_tweet(markov, prompt)
      status = api.update_status(status=tweet)
  except IOError:
      print('no internet')


if __name__ == "__main__":
    mins = 0
    while mins != 20:
        print(">", mins)
        main()
        time.sleep(60*2)
        mins += 1*2


