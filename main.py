from flask import Flask
from flask_restful import Api, Resource, reqparse
import requests

app = Flask(__name__)
api = Api(app)

users = {}

args_post_parse = reqparse.RequestParser()
args_post_parse.add_argument('first_name', type=str, required=True)
args_post_parse.add_argument('second_name', type=str, required=True)
args_post_parse.add_argument('age', type=int, required=True)

args_update_parse = reqparse.RequestParser()
args_update_parse.add_argument('first_name', type=str)
args_update_parse.add_argument('second_name', type=str)
args_update_parse.add_argument('age', type=int)

args_user_post_parse = reqparse.RequestParser()
args_user_post_parse.add_argument('data', type=str)

args_amount = reqparse.RequestParser()
args_amount.add_argument('currency', type=int)


class BankAccountWork(Resource):
    def post(self, user_id):
        args = args_amount.parse_args()
        users[user_id]['currency'] = args['currency']
        return users[user_id]

    def get(self, user_id):
        return users[user_id]['currency']

    def patch(self, user_id, country):
        answer = requests.get('https://www.cbr-xml-daily.ru/daily_json.js')
        json_format = answer.json()
        value = json_format['Valute'][country]["Value"]

        users[user_id]['currency'] = users[user_id]['currency'] * value

        return users[user_id]['currency']


class PostWork(Resource):
    def post(self, post_id, user_id):
        args = args_user_post_parse.parse_args()
        users[user_id]['posts'][post_id] = {'data': args['data']}
        return users[user_id]

    def get(self, user_id):
        return users[user_id]['posts']

    def patch(self, post_id, user_id):
        args = args_user_post_parse.parse_args()
        if args['data']:
            users[user_id]['posts'][post_id]['data'] = args['data']
        return users[user_id]['posts'][post_id]

    def delete(self, post_id, user_id):
        del users[user_id]['posts'][post_id]
        return ''


class UsersWork(Resource):
    def get(self):
        if not users:
            return {'message': 'Add some users!'}
        return users

    def get(self, user_id):
        if user_id in users:
            return users[user_id]
        else:
            return {'message': 'The user with this id is not exist'}

    def post(self, user_id):
        args = args_post_parse.parse_args()
        users[user_id] = args
        users[user_id]['posts'] = {}
        return users[user_id]

    def patch(self, user_id):
        args = args_update_parse.parse_args()
        if args['first_name']:
            users[user_id]['first_name'] = args['first_name']
        if args['second_name']:
            users[user_id]['second_name'] = args['second_name']
        if args['age']:
            users[user_id]['age'] = args['age']
        return users[user_id]

    def delete(self, user_id):
        del users[user_id]
        return ''


api.add_resource(UsersWork, '/api/users', '/api/users/<int:user_id>')
api.add_resource(PostWork, '/api/users/<int:user_id>/posts/<int:post_id>', '/api/users/<int:user_id>/posts')
api.add_resource(BankAccountWork, '/api/users/<int:user_id>/total', '/api/users/<int:user_id>/total/<string:country>')

if __name__ == '__main__':
    app.run(debug=True)
