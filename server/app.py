from flask import Flask, jsonify, request, abort
from flask_cors import CORS, cross_origin
from controller import processExample, processBarChart, processParallelData, processKMSurvivalCurveData, processKMSurvivalCurveSerialData

app = Flask(__name__)
CORS(app)

@app.route("/")
@cross_origin()
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/fetchExample", methods=["GET", "POST"])
@cross_origin()
def fetchExample():
    if request.method == "GET": # handling GET request
        points, cluster_names = processExample()
        resp = jsonify(data=points, clusters=cluster_names)
        return resp
    else: 
        # handling POST request, which is only effective when ExampleWithInteractions.vue is loaded
        request_context = request.get_json() # JSON object
        mfg = request_context['method']
        #print("fetchExample() " + mfg, flush=True)
        points, cluster_names = processExample(mfg)
        resp = jsonify(data=points, clusters=cluster_names)
        return resp

    
@app.route("/fetchBarPlotData", methods=["GET", "POST"])
@cross_origin()
def fetchBarPlotData():
    if request.method == "GET": # handling GET request
        points, cluster_names = processBarChart()
        resp = jsonify(data=points, clusters=cluster_names)
        return resp
    else: 
    # handling POST request, which is only effective when ExampleWithInteractions.vue is loaded
        request_context = request.get_json() # JSON object
        method = request_context['method']
        points, cluster_names = processBarChart(method)
        resp = jsonify(data=points, clusters=cluster_names)
        return resp


@app.route("/fetchParallelData", methods=["GET", "POST"])
@cross_origin()
def fetchParallelData():
    if request.method == "GET": # handling GET request
        points, cluster_names, columns = processParallelData()
        resp = jsonify(data=points, clusters=cluster_names, columns=columns)
        return resp
    else: 
    # handling POST request, which is only effective when ExampleWithInteractions.vue is loaded
        request_context = request.get_json() # JSON object
        manufacturer = request_context['manufacturer']
        points, cluster_names, columns = processParallelData(manufacturer)
        resp = jsonify(data=points, clusters=cluster_names, columns=columns)
        return resp


@app.route("/fetchKMSurvivalCurveData", methods=["GET"])
@cross_origin()
def fetchKMSurvivalCurveData():
    if request.method == "GET": # handling GET request
        try:
            #points, cluster_names, columns = processKMSurvivalCurveData()
            # resp = jsonify(data=points, clusters=cluster_names, columns=columns)
            points, cluster_names = processKMSurvivalCurveData()
            resp = jsonify(data=points, clusters=cluster_names)
            return resp

        except Exception as e:
            abort(500, description=str(e))

    else:
        abort(500, description=str(e))

@app.route("/fetchKMSurvivalCurveSerialData", methods=["GET", "POST"])
@cross_origin()
def fetchKMSurvivalCurveSerialData():
    if request.method == "GET": # handling GET request
        try:
            # handling POST request, which is only effective when ExampleWithInteractions.vue is loaded
            manufacturer = request.args.get('manufacturer')
            points, cluster_names, capacity_clusters,life_exp = processKMSurvivalCurveSerialData(manufacturer)
            resp = jsonify(data=points, clusters=cluster_names,capacity_clusters=capacity_clusters,life_exp=life_exp)
            # points, cluster_names, columns = processKMSurvivalCurveData(manufacturer)
            # resp = jsonify(data=points, clusters=cluster_names, columns=columns)
            return resp

        except Exception as e:
            abort(500, description=str(e))

    else:
        try:
            request_context = request.get_json() # JSON object
            manufacturer = request_context['manufacturer']
            points, cluster_names,capacity_clusters,life_exp  = processKMSurvivalCurveSerialData(manufacturer)
            resp = jsonify(data=points, clusters=cluster_names,capacity_clusters=capacity_clusters,life_exp=life_exp)
            # points, cluster_names, columns = processKMSurvivalCurveData(manufacturer)
            # resp = jsonify(data=points, clusters=cluster_names, columns=columns)
            return resp

        except Exception as e:
            abort(500, description=str(e))

if __name__ == "__main__":
    app.run(port=3100, debug=True)