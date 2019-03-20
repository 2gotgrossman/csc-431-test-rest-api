from flask import Flask, jsonify
from flask import abort
from flask import make_response
from flask import request
from flask import send_file
import os

import data

HAZARD_TYPES = ['volcanoes', 'earthquakes']
SUPPORTED_IMAGE_TYPES = ["geo_backscatter", "geo_coherence",
               "geo_interferogram", "ortho_backscatter",
               "ortho_coherence", "ortho_interferogram"]

SUPPORTED_SATELLITES = ['satellite_id0', 'satellite_id1']

app = Flask(__name__)

@app.route('/api/<string:hazard_type>', methods=['GET'])
def get_hazards_summary_info(hazard_type):
    if hazard_type == 'volcanoes':
        return jsonify(data.get_all_volcano_summary_info())
    else:
        abort(404, "Hazard Type {0} does not exist.".format(hazard_type))

@app.route('/api/<string:hazard_type>/<string:hazard_id>', methods=['GET'])
def get_hazard_info_page(hazard_type, hazard_id):
    # Check if hazard_type is legit
    if hazard_type not in HAZARD_TYPES:
        abort(404, "Hazard Type {0} does not exist.".format(hazard_type))
    elif hazard_type == 'earthquakes':
        abort(500, "The earthquake Hazard Type is currently not supported")
    elif hazard_type == 'volcanoes':
        if hazard_id != data.HAZARD_INFO_TEMPLATE['hazard_id']:
            abort("The hazard with id {0} does not exist as a {1} Hazard Type.".format(hazard_id, hazard_type))
        else:
            image_types_requested = request.args.get('image_types')

            types = set()
            if image_types_requested is not None:
                image_types_requested = image_types_requested.split(",")
                for image_type in image_types_requested:
                    if image_type in SUPPORTED_IMAGE_TYPES:
                        types.add(image_type)
                if len(types) == 0:
                    abort(400, "None of the following image types are supported: '{0}'".format(str(image_types_requested)))
            print("TYPES:", types)
            # Check that these variables are of the correct type
            satellites_requested = request.args.get('satellites')
            start_date, end_date = request.args.get('start_date'), request.args.get('end_date')

            satellites = set()
            if satellites_requested is not None:
                satellites_requested = satellites_requested.split(',')
                for satellite in satellites_requested:
                    if satellite in SUPPORTED_SATELLITES:
                        satellites.add(satellite)
                if len(satellites) == 0:
                    abort(400, "None of the following satellites are supported: '{0}'".format(str(satellites_requested)))

            if start_date is not None:
                if not len(start_date) == 8 or not start_date.isdigit():
                    abort(400, "Incorrectly formatted start_date: {0}".format(start_date))
            if end_date is not None:
                if not len(end_date) == 8 or not end_date.isdigit():
                    abort(400, "Incorrectly formatted end_date: {0}".format(end_date))

            max_num_images = request.args.get('max_num_images')
            if max_num_images is None:
                max_num_images = 0
            elif not max_num_images.isdigit():
                abort(400, "Parameter 'max_num_images' must be an integer")
            else:
                max_num_images = int(max_num_images)


            # Build request
            return jsonify(data.get_volcano_hazard_info_by_id(hazard_id, types, satellites, max_num_images))

@app.route('/api/images/<string:image_id>')
def get_image(image_id):
    print("YO ITS ME", os.path.realpath(__file__))
    location = data.get_image_file_location(image_id)
    print("AFTER YO IT'S ME. location: ", location, type(location))

    if location is None:
        abort(404, "Image with image id {0} does not exist.".format(str(image_id)))
    else:
        file_loc = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')
        print("FILE LOCATION", file_loc)
        return send_file(os.path.join(file_loc, location), as_attachment=True, mimetype='image/jpeg')


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': str(error)}), 404)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': str(error)}), 404)

if __name__ == '__main__':
    app.run(debug=True)
    #app.run(host="0.0.0.0", port=80)
