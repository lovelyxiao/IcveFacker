import json

import requests


class IcveMooc:
    URL_LOGIN = 'https://mooc.icve.com.cn/portal/LoginMooc/loginSystem'
    URL_COURSE_LIST = 'https://mooc.icve.com.cn/portal/course/getCourseOpenList'
    URL_PROCESS_LIST = 'https://mooc.icve.com.cn/study/learn/getProcessList'
    URL_TOPIC_LIST = 'https://mooc.icve.com.cn/study/learn/getTopicByModuleId'
    URL_CELL_LIST = 'https://mooc.icve.com.cn/study/learn/getCellByTopicId'
    URL_STUDY_VIEW = 'https://mooc.icve.com.cn/study/learn/viewDirectory'
    URL_STUDY_PROCESS = 'https://mooc.icve.com.cn/study/learn/statStuProcessCellLogAndTimeLong'

    URL_EXAM_LIST = 'https://mooc.icve.com.cn/study/workExam/getWorkExamList'
    URL_EXAM_PREVIEW = 'https://mooc.icve.com.cn/study/workExam/workExamPreview'
    URL_EXAM_ANSWER = 'https://mooc.icve.com.cn/study/workExam/onlineHomeworkAnswer'
    URL_EXAM_SAVE = 'https://mooc.icve.com.cn/study/workExam/workExamSave'

    def __init__(self):
        self._session = requests.session()
        self._info = None  # type: dict

    def login(self, username, password):
        data = {
            'userName': username,
            'password': password,
        }
        resp = self._session.post(IcveMooc.URL_LOGIN, data)
        self._info = resp.json()  # type: dict
        return self._info

    @property
    def info(self):
        return self._info

    @property
    def course_list(self):
        resp = self._session.get(IcveMooc.URL_COURSE_LIST)
        resp_data = resp.json()  # type: dict
        return resp_data.get('list')

    def module_list(self, coid):
        data = {
            'courseOpenId': coid,
        }
        resp = self._session.post(IcveMooc.URL_PROCESS_LIST, data)
        resp_data = resp.json()  # type: dict
        return resp_data.get('proces').get('moduleList')

    def topic_list(self, coid, mid):
        data = {
            'courseOpenId': coid,
            'moduleId': mid,
        }
        resp = self._session.post(IcveMooc.URL_TOPIC_LIST, data)
        resp_data = resp.json()  # type: dict
        return resp_data.get('topicList')

    def cell_list(self, coid, tid):
        data = {
            'courseOpenId': coid,
            'topicId': tid,
        }
        resp = self._session.post(IcveMooc.URL_CELL_LIST, data)
        resp_data = resp.json()  # type: dict
        return resp_data.get('cellList')

    def study_view(self, coid, cid, mid):
        data = {
            'courseOpenId': coid,
            'cellId': cid,
            'fromType': 'stu',
            'moduleId': mid,
        }

        resp = self._session.post(IcveMooc.URL_STUDY_VIEW, data)
        resp_data = resp.json()  # type: dict
        return resp_data

    def study_process(self, coid, mid, cid, v_len, v_time, s_type):
        data = {
            'courseId': '',
            'courseOpenId': coid,
            'moduleId': mid,
            'cellId': cid,
            'auvideoLength': v_len,
            'videoTimeTotalLong': v_time,
            'sourceForm': s_type,
        }

        resp = self._session.post(IcveMooc.URL_STUDY_PROCESS, data)
        resp_data = resp.json()  # type: dict
        return resp_data.get('isStudy', False)

    def exam_list(self, coid, e_type):
        data = {
            'workExamType': e_type,
            'courseOpenId': coid,
        }
        resp = self._session.post(IcveMooc.URL_EXAM_LIST, data)
        resp_data = resp.json()  # type: dict
        return resp_data.get('list')

    def exam_preview(self, coid, eid, e_type):
        data = {
            'courseOpenId': coid,
            'workExamId': eid,
            'agreeHomeWork': 'agree',
            'workExamType': e_type,
        }

        resp = self._session.post(IcveMooc.URL_EXAM_PREVIEW, data)
        resp_data = resp.json()  # type: dict
        return resp_data

    def exam_answer(self, qid, answer, q_type, uid, e_type):
        data = {
            'studentWorkId': '',
            'questionId': qid,
            'workExamType': e_type,
            'online': '1',
            'answer': answer,
            'userId': '',
            'questionType': q_type,
            'paperStuQuestionId': '',
            'uniqueId': uid,
        }

        resp = self._session.post(IcveMooc.URL_EXAM_ANSWER, data)
        resp_data = resp.json()  # type: dict
        return resp_data['allDo']

    def exam_save(self, coid, eid, uid):
        data = {
            'courseOpenId': coid,
            'workExamId': eid,
            'uniqueId': uid,
            'workExamType': '0',
            'paperStructUnique': '',
            'useTime': '2333',
        }

        resp = self._session.post(IcveMooc.URL_EXAM_SAVE, data)
        resp_data = resp.json()  # type: dict
        return resp_data


def finish_course(im: IcveMooc, coid):
    for module in im.module_list(coid):
        mid = module['id']
        if module['percent'] < 100:
            print('module', module)
            for topic in im.topic_list(coid, mid):
                if topic['studyStatus'] != 1:
                    print('topic', topic)
                    for cell in im.cell_list(coid, topic['id']):
                        if 'childNodeList' in cell.keys() and len(cell['childNodeList']) > 0:
                            for child in cell['childNodeList']:
                                if not child['isStudyFinish']:
                                    cid = child['Id']
                                    data = im.study_view(coid, cid, mid)['courseCell']
                                    s_type = '888' if data['IsAllowDownLoad'] else '1229'
                                    result = im.study_process(coid, mid, cid, data['VideoTimeLong'],
                                                              data['VideoTimeLong'],
                                                              s_type)
                                    print('cell_child', result, child['cellName'])
                        else:
                            if not cell['isStudyFinish']:
                                cid = cell['Id']
                                data = im.study_view(coid, cid, mid)['courseCell']
                                s_type = '888' if data['IsAllowDownLoad'] else '1229'
                                result = im.study_process(coid, mid, cid, data['VideoTimeLong'],
                                                          data['VideoTimeLong'],
                                                          s_type)
                                print('cell', result, cell['cellName'])


def finish_exam(im: IcveMooc, coid, e_type):
    for exam in im.exam_list(coid, e_type):
        if exam['IsDoExam'] == 0 or exam['getScore'] < 100:
            print(exam)
            eid = exam['Id']
            data = im.exam_preview(coid, eid, e_type)
            uid = data['uniqueId']

            questions = data['paperData']['questions']
            if questions is None:
                questions = json.loads(data['workExamData'])['questions']

            for question in questions:
                result = im.exam_answer(question['questionId'], question['Answer'], question['questionType'], uid,
                                        e_type)
                print(result, question['Title'])

            im.exam_save(coid, eid, uid)


def finish_all(im: IcveMooc):
    for course in im.course_list:
        coid = course['id']
        print('course', course)
        finish_course(im, coid)
        finish_exam(im, coid, 0)
        finish_exam(im, coid, 1)


username = input('username:')
password = input('password:')

im = IcveMooc()
im.login(username, password)
print(im.info)
finish_all(im)
