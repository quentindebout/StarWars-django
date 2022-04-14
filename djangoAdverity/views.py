import csv
import os

from django.http import HttpResponse
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
import petl
from .models import DownloadedDataset
import requests
from io import StringIO


from djangoAdverity.utils import fetch_all_data, merge_and_transform, store_data


class SwapiView(View):
    def get(self, request, *args, **kwargs):
        try:
            # fetching all people (82 people => 9 requests because 10 object is the limit for one request)
            # number of requests cannot be optimized, except if I am wrong ...
            people = fetch_all_data('people')

            # fetching all planet (60 planets => 6 requests)
            # not very elegant but people seem to be born on many planets
            # going for a set containing the planet ids and requesting them one by one would be very slow
            # BUT it might be possible to save one request here by avoiding requesting useless planets. See below

            planets = fetch_all_data('planets')

            """The following commented line shows most of the idea I have to try to reduce number of requests
            # But I did not do the whole implementation (API requests logic)
            # NB : it would work only if page 1 contains id 1 to 10, page 2 11-20, etc, with no "holes".

            # first create a set containing the planets ids where people are born on. 
            # I chose a set to remove duplicate.
            # This set will contain 49 elements here, so we may have a chance to save a request ! :
            planets_ids = {person['homeworld'].replace(SWAPI_URL+"planets/", "")[:-1] for person in people}

            # then by mostly performing an integer division on each element by 10 , we can get the page that contains
            # the planet.
            # we keep all the results in a set to again avoid duplicate, and we end up with a set equals to 
            # {1, 2, 3, 4, 5, 6}. We cannot save any request here because all 6 pages are needed ...
            page_ids = {(int(planets_id)-1)//10 + 1 for planets_id in planets_ids} """

        except requests.exceptions.RequestException as e:
            print("Error when requesting swapi :", e)
            return HttpResponse(status=503)
        else:
            people = merge_and_transform(people, planets)

            response = HttpResponse(
                content_type='text/csv',
                headers={'Content-Disposition': 'attachment; filename="people.csv"'},
            )

            # fill response with csv data
            writer = csv.DictWriter(response, people[0].keys())
            writer.writeheader()
            writer.writerows(people)

            # store csv as a string in db
            # csv.DictWriter method add a '\r' character at every line causing issue with petl later, so  I remove it
            store_data(response.content.decode().replace("\r", ""))

            return response


class IndexView(ListView):
    template_name = 'index.html'
    model = DownloadedDataset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        for element in context['object_list']:
            element.date = element.date.strftime('%b %d,%Y  %H:%M:%S')
        # For the index page, I just need the date of the downloaded dataset as well as their id in order to redirect
        # the user when he clicks on it. IndexView extends ListView, which is doing most of the job here.
        return context


def check_parameters(row_nb, group_by, fields):
    # verifying that url parameters are compliant
    valid_group_by = None
    if group_by is not None and type(group_by) is str:
        group_by = group_by.split(',')

        # group_by parameters should be headers (height, homeworld, gender, etc)
        valid_group_by = [field for field in group_by if field in fields]

    valid_row_nb = None
    if row_nb is not None and row_nb.isdigit() and int(row_nb) > 0:
        valid_row_nb = int(row_nb)

    return valid_group_by, valid_row_nb


class TableView(DetailView):
    model = DownloadedDataset
    template_name = 'table.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        row_nb = self.request.GET.get('nb')
        group_by = self.request.GET.get('group')

        # creating a file from csv string because petl needs a file to execute fromcsv method
        # there is probably a cleaner way
        with open('csv.txt', 'w') as f:
            f.write(context['object'].csv)
            f.close()

        table = petl.fromcsv('csv.txt')


        # header corresponding to the first line of the table (may be modified later)
        context['header'] = petl.header(table)

        # header that will be used for the button list for the Value Count functionality (constant)
        context['button_header'] = context['header']

        group_by, row_nb = check_parameters(row_nb, group_by, context['header'])

        # as the 2 functionalities can be separated, giving priority to Value count :
        if group_by:

            if len(group_by) == 1:
                # have to do this because of petl
                group_by = group_by[0]

            table = petl.aggregate(table, group_by, aggregation={'count': len})
            context['header'] = petl.header(table)
            context['object'].csv = petl.data(table)
        else:
            context['object'].csv = petl.data(table, row_nb or 10)
        return context
