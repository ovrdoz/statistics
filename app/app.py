#!/usr/bin/python

import os, json
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import label

database_uri = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
    dbuser=os.environ['DBUSER'],
    dbpass=os.environ['DBPASS'],
    dbhost=os.environ['DBHOST'],
    dbname=os.environ['DBNAME']
)

app = Flask(__name__)
app.config.update(
    SQLALCHEMY_DATABASE_URI=database_uri,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

# initialize the database connection
db = SQLAlchemy(app)

@app.route('/api-summary/<month>/<int:page>')
def view_summary_by_month(month,page=1):
    page=1
    per_page = 10

    from models import HubSummary, HubEventStatus

    date = request.view_args['month']
    page = request.view_args['page']

    _result = db.session.query(HubSummary)\
    .paginate(page, per_page, error_out=False).items
    
    return render_template('api_summary_top.html', result=_result)

@app.route('/api-summary/<date>/<time>/<int:page>')
def view_web_summary(date, time, page=1):
    per_page = 10

    from models import HubSummary, HubEventStatus

    date = request.view_args['date']
    time = request.view_args['time']
    page = request.view_args['page']

    _result = db.session.query(HubSummary)\
    .filter(HubSummary.cycle=='%s %s:00:00' % (date,time))\
    .paginate(page, per_page, error_out=False).items
    
    return render_template('api_summary_list.html', result=_result)

@app.route('/api/reports/summary', methods = ['POST'])
def view_api_summary():

    data = json.loads(request.data)
    
    _type     = data.get('type')
    _date     = data.get('date')
    _page     = data.get('page')
    _per_page = data.get('per_page')

    sql = None
    if _type == 'hour':
        sql = db.text("SELECT DISTINCT su.id, to_char(su.cycle, 'YYYY-MM-DD HH24:MI') as period, application_id, api_id, su.resource as resource, su.resource_total as resource_total, (select sum(st.status_total) from api_status st where st.status_code < 300 and su.id = st.summary_id ) as sucesso, (select sum(st.status_total) from api_status st where st.status_code > 300 and su.id = st.summary_id ) as erro FROM api_summary su WHERE  resource='Crypto - Descriptografa' group by su.id, to_char(su.cycle, 'YYYY-MM-DD HH24:MI') ORDER BY period DESC limit 10")
    if _type == 'day':
        sql = db.text("SELECT DISTINCT su.id, to_char(su.cycle, 'YYYY-MM-DD') as period, application_id, api_id, su.resource as resource, su.resource_total as resource_total, (select sum(st.status_total) from api_status st where st.status_code < 300 and su.id = st.summary_id ) as sucesso, (select sum(st.status_total) from api_status st where st.status_code > 300 and su.id = st.summary_id ) as erro FROM api_summary su WHERE  resource='Crypto - Descriptografa' group by su.id, to_char(su.cycle, 'YYYY-MM-DD') ORDER BY period DESC limit 10")
    if _type == 'month':
        sql = db.text("SELECT DISTINCT su.id, to_char(su.cycle, 'YYYY-MM') as period, application_id, api_id, su.resource as resource, su.resource_total as resource_total, (select sum(st.status_total) from api_status st where st.status_code < 300 and su.id = st.summary_id ) as sucesso, (select sum(st.status_total) from api_status st where st.status_code > 300 and su.id = st.summary_id ) as erro FROM api_summary su WHERE  resource='Crypto - Descriptografa' group by su.id, to_char(su.cycle, 'YYYY-MM') ORDER BY period DESC limit 10")
    
    if sql is not None:   
        _result = db.engine.execute(sql)
        return jsonify( {'summary': [dict(r) for r in _result]})
    else:
        return jsonify( {'error': 'please, filter by (hour, day or month)'} ), 403

@app.route('/api/jobs/summary', methods = ['GET'])
def view_job_summary():
     
    from datetime import datetime, timedelta
    from elasticsearch import Elasticsearch
    from elasticsearch_dsl import Search
    from elasticsearch_dsl.query import Range
    from models import HubSummary, HubEventStatus, HubApi, HubApplication, HubEntrypoint

    #today       = (datetime.now() + timedelta(hours=-1)).strftime("%Y%m%d")
    #start_date  = (datetime.now() + timedelta(hours=-1)).strftime("%Y-%m-%dT%H:00:00.000Z") #RFC 3339 format
    #end_date    = datetime.now().strftime("%Y-%m-%dT%H:00:00.000Z") #RFC 3339 format
        
    today       = "20181101"
    start_date  = "2018-11-01T00:00:00.000Z"
    end_date    = "2018-11-02T00:00:00.000Z"

    last = db.session.query(HubSummary)\
    .filter(HubSummary.cycle == start_date).first()
    
    if last is not None:
        return jsonify({'warning': 'this job has already been done for time: %s' % (last.cycle)}), 406, {'ContentType':'application/json'}

    client = Elasticsearch(["http://elasticapi.santanderbr.corp:9200"])
    
    s = Search(using=client, index="events-santander-"+today)\
    .params(request_timeout=300)\
    .source(False)\
    .query("query_string",query="_entrypoint.id: 3 and _entrypoint.id: 6", analyze_wildcard=True)\
    .query(Range(** {'entries.entrypoint.startedDateTime': {'gte': '%s' % (start_date), 'lt': '%s' % (end_date)}} ))

    s.aggs.bucket("histogram", "date_histogram", field="entries.entrypoint.startedDateTime", interval="1h", min_doc_count=1, format="yyyy-MM-dd HH:mm:ss")\
        .bucket("entrypoint", "terms", script="doc['_entrypoint.id'].value +'|'+ doc['_entrypoint.name'].value")\
        .bucket("apk", "terms", script="doc['_clientApplication.key'].value +'|'+ doc['_clientApplication.name'].value")\
        .bucket("app", "terms", script="doc['_clientApplication.id'].value +'|'+ doc['_clientApplication.name'].value")\
        .bucket("api", "terms", script="doc['_api.id'].value +'|'+ doc['_api.name'].value")\
        .bucket("resource", "terms", field="_resource.name", order={"_count":"desc"})\
        .bucket("method", "terms", field="_resourceMethod.httpVerb")\
        .bucket("entrypoint_event", "terms", field="entries.entrypoint.response.status", order={"_count":"desc"})\
        .metric("entrypoint_avg", "avg", field="entries.entrypoint.time")\
        .bucket("endpoint_event", "terms", field="entries.endpoint.response.status", order={"_count":"desc"})\
        .metric("endpoint_avg", "avg", field="entries.endpoint.time")

    print(json.dumps(s.to_dict(), sort_keys=True, indent=4))

    print ("start query es: %s" % datetime.now())
    response = s.execute()
    print ("start insert's: %s" % datetime.now())
    try:
        for histogram in response.aggregations.histogram.buckets:
            for ent in histogram.entrypoint.buckets:
                for apk in ent.apk.buckets:
                    for app in apk.app.buckets:
                        for api in app.api.buckets:
                            for resource in api.resource.buckets:
                                keyId,keyName = apk.key.split("|")
                                apiId,apiName = api.key.split("|")
                                appId,appName = app.key.split("|")
                                entId,entName = ent.key.split("|")
                                obj_summary = HubSummary(application_key=keyId, application_key_name=keyName, application_key_total=apk.doc_count, application_id=appId, application_total=app.doc_count, api_id=apiId, api_total=api.doc_count, resource=resource.key, resource_total=resource.doc_count, entrypoint_id=entId, cycle=histogram.key_as_string, owner_id=1)
                                for method in resource.method.buckets:
                                    for entrypoint_event in method.entrypoint_event.buckets:
                                        for endpoint_event in entrypoint_event.endpoint_event.buckets:
                                            obj_status = HubEventStatus(entrypoint_method=method.key, entrypoint_status_code=entrypoint_event.key, entrypoint_status_total=entrypoint_event.doc_count, entrypoint_time_avg=entrypoint_event.entrypoint_avg.value,endpoint_status_code=endpoint_event.key, endpoint_status_total=endpoint_event.doc_count, endpoint_time_avg=endpoint_event.endpoint_avg.value) #removed percentage=((status.doc_count * 100)/ resource.doc_count)
                                            obj_summary.event_status.append(obj_status)
                                
                                obj_api = HubApi(id=apiId, name=apiName)
                                obj_app = HubApplication(id=appId, name=appName)
                                obj_ent = HubEntrypoint(id=entId, name=entName)

                                db.session.merge(obj_api)
                                db.session.merge(obj_app)
                                db.session.merge(obj_ent)
                                db.session.add(obj_summary)
                                db.session.commit()

        return jsonify({'success': 'ok'}), 200

    except Exception, e:
        return jsonify({'error': str(e)})
