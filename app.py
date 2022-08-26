from flask import Flask, render_template, send_from_directory, request, Response, jsonify
import json
import pandas as pd
from flask_cors import CORS, cross_origin
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask_swagger import swagger
# from flask_restplus import Api, apidoc
# # from flask_restplus import *
# # from werkzeug.utils import cached_property
# import werkzeug
# import cached_property
# werkzeug.cached_property = werkzeug.utils.cached_property

# try:
#     from flask_restplus import Resource, Api, apidoc
# except ImportError:
#     import werkzeug
#     werkzeug.cached_property = werkzeug.utils.cached_property
#     from flask_restplus import Resource, Api, apidoc

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'supersecretkey'

# api = Api(app)
#
# @api.documentation
# def custom_ui():
#     return apidoc.ui_for(api)

# @app.route("/spec")
# def spec():
#     swag = swagger(app)
#     swag['info']['version'] = "1.0"
#     swag['info']['title'] = "My API"
#     return jsonify(swag)

@app.route('/', methods=['GET'])
@cross_origin()
def hello():
    return "Hello World"


@app.route('/post_form', methods=['POST'])
@cross_origin()
def process_form():
    data = json.loads(request.data)

    keys = ['jdYOE', 'jdSkillset', 'jdDesig']
    JD_dict = {x: data[x] for x in keys}

    keys = ['candiYOE', 'candiSkillset', 'candiDesig']
    candi_dict = {x: data[x] for x in keys}

    candi_df = pd.DataFrame([candi_dict])
    JD_df = pd.DataFrame([JD_dict])

    df = pd.DataFrame(columns=["Years of Experience", "Skillset", "Designation"])
    JD_df.columns = ['Years of Experience', 'Skillset', 'Designation']
    candi_df.columns = ['Years of Experience', 'Skillset', 'Designation']
    df = pd.concat([df, JD_df, candi_df], axis=0)
    df["Years of Experience"].fillna("Not Mentioned", inplace=True)
    df["Skillset"].fillna("Not Mentioned", inplace=True)
    df["Designation"].fillna("Not Mentioned", inplace=True)
    df.reset_index(inplace=True, drop=True)

    a_list = []
    for j in range((df.shape[0])):
        cur_row = []
        for k in range(df.shape[1]):
            cur_row.append(df.iat[j, k])
        a_list.append(cur_row)

    jd = a_list[0]
    res = a_list[1]

    jd_ = [' '.join(jd)][0]
    res_ = [' '.join(res)][0]

    jd_ = jd_.lower()
    res_ = res_.lower()

    text = [jd_, res_]
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(text)

    cos_sim = round(cosine_similarity(count_matrix)[0][1] * 100, 2)

    status = []
    if cos_sim >= 70:
        sta = "Selected"
        status.append(sta)

    elif cos_sim > 50 and cos_sim < 70:
        sta = "Hold"
        status.append(sta)
    else:
        sta = "Rejected"
        status.append(sta)

    remarks = []
    if status[0] == "Selected":
        rem_ = "JD is matched with Candidate's skills set"
        remarks.append(rem_)
    elif status[0] == "Hold":
        rem_ = "JD is partially matched with Candidate's skills set"
        remarks.append(rem_)
    else:
        rem_ = "JD is not matched with Candidate's skills set"
        remarks.append(rem_)

    name = data.get("candiName")
    jdNum = data.get("jdNum")

    dict_ = {"Name": name, "JD_Number": jdNum, "Percentage": cos_sim, "Status": status[0], "Remarks": remarks[0]}
    return (dict_)


if __name__ == '__main__':
    Response(headers={'Access-Control-Allow-Origin': '*'})
    app.run(debug=True)
