import os
import uuid
import threading

from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory
)

from dotenv import load_dotenv

from pipeline import run_pipeline


load_dotenv()


app = Flask(
    __name__,
    static_folder="static"
)

app.config["UPLOAD_DIR"] = "uploads"

os.makedirs(
    app.config["UPLOAD_DIR"],
    exist_ok=True
)


jobs = {}


@app.route("/")
def index():

    return send_from_directory(
        "static",
        "index.html"
    )


@app.route(
    "/upload",
    methods=["POST"]
)
def upload():

    if "image" not in request.files:

        return jsonify(
            error="No file"
        ), 400

    f = request.files["image"]

    job_id = str(
        uuid.uuid4()
    )[:8]

    path = os.path.join(
        app.config["UPLOAD_DIR"],
        f"{job_id}_{f.filename}"
    )

    f.save(path)

    jobs[job_id] = {
        "stages": [],
        "done": False,
        "result": None
    }


    def worker():

        job = jobs[job_id]

        try:

            for item in run_pipeline(path):

                if item is None:

                    job["done"] = True
                    return

                if "url" in item:

                    job["result"] = item

                else:

                    job["stages"].append(
                        item
                    )

        except Exception as e:

            print(
                "PIPELINE ERROR:",
                repr(e),
                flush=True
            )

            job["stages"].append({
                "name": "error",
                "status": "fail",
                "detail": str(e)[:60]
            })

        finally:

            job["done"] = True


    threading.Thread(
        target=worker,
        daemon=True
    ).start()

    return jsonify(
        job_id=job_id
    )


@app.route(
    "/status/<job_id>"
)
def status(job_id):

    return jsonify(
        jobs.get(
            job_id,
            {
                "error": "unknown job"
            }
        )
    )


if __name__ == "__main__":

    app.run(
        debug=False,
        port=5000
    )