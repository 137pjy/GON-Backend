from flask import Blueprint,request,jsonify
from control.teacher_mgmt import Teacher
import bcrypt
from model.mongodb import conn_mongodb
from bson.json_util import dumps
import json
from bson import ObjectId

teacher = Blueprint('teacher',__name__)

mongo_db = conn_mongodb()

@teacher.route("/",methods=['POST','GET'])
def teacher_add():
    if request.method == 'POST':
        new_user = request.get_json()
        
        if not Teacher.check_is_unique(new_user['id']):
            return jsonify({"code":"400", "message" : "아이디가 중복입니다."})
        else:
            #입력받은 비밀번호 암호화하여 db저장
            new_user['pw'] = bcrypt.hashpw(new_user['pw'].encode('UTF-8'),bcrypt.gensalt())
            
            
            # Teacher.add_teacher(new_user['id'],new_user['pw'],new_user['account'],new_user['full_name'],
            #                     new_user['phone_num'],new_user['course_id']) teacher조회시 course정보를 같이 출력하기 테스트를 위해 course_id 추가
            Teacher.add_teacher(new_user['id'],new_user['pw'],new_user['account'],new_user['full_name'],
                                new_user['phone_num'])

            return jsonify({'code':"200",'message':'선생님 회원가입 성공!'})
    # elif request.method == 'GET':
    #     page =int(request.args.get('page'))
    #     size = int(request.args.get('size'))
        
    #     result = mongo_db.teacher.find().sort("id",1).skip(size*(page-1)).limit(size)
                
    #     serialized_data = dumps(result, default=str)#dumps() : 딕셔너리 자료형을 JSON 문자열로 만든다.
    #     json_data = json.loads(serialized_data)#loads() : JSON 문자열을 딕셔너리로 변환
        
    #     return json_data
    elif request.method == 'GET':
        page =int(request.args.get('page'))
        size = int(request.args.get('size'))
        
        result = mongo_db.teacher.find().sort("id",1).skip(size*(page-1)).limit(size)
        
        serialized_data = dumps(result, default=str)#dumps() : 딕셔너리 자료형을 JSON 문자열로 만든다.
        
        
        json_data = json.loads(serialized_data)#loads() : JSON 문자열을 딕셔너리로 변환
        
        for data in json_data:
            student_id = data['course_id']#이후 course가 생성되면 student_id가 아니라 course_id로 바꾸기
            student_row = mongo_db.student.find_one({'_id':ObjectId(student_id)})#이후 course가 생성되면 student_row가 아니라 course_row로 바꾸기
            data['courses'] = [{
                'student_name' : student_row['full_name'],
                'student_id' : student_row['id']
            }]
              
        return json_data
    
@teacher.route('/<teacher_id>', methods = ['DELETE','PATCH'])
def teacher_crud(teacher_id):
    
    if request.method == "DELETE":
        Teacher.delete_teacher(teacher_id)
        return jsonify({"code":"200","message":"삭제가 완료되었습니다."})
    
    if request.method == "PATCH":
        input_data = request.json
        
        if not Teacher.check_is_unique(input_data['id']):
            return jsonify({"code":"400", "message" : "아이디가 중복입니다."})
        else:
            input_data['pw'] = bcrypt.hashpw(input_data['pw'].encode('UTF-8'),bcrypt.gensalt())
            target = {"_id":ObjectId(teacher_id)}

            new_data = {"$set":{
                'id': input_data['id'],
                 'hashed_pw' : input_data['pw'],
                'full_name' : input_data['full_name'],
                'phone_num' : input_data['phone_num']
                }}
            print("hello")
            result = Teacher.edit_teacher(target,new_data)
        
            if result.modified_count == 0:
                return jsonify({"code":"400","message":"수정할 선생님을 찾을 수 없습니다."})
            else:
                return jsonify({'code':"200",'message':'선생님정보 수정성공!'})
                