from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from gpt_index import GPTSimpleVectorIndex

from datetime import datetime

from .functions import interpret_text, read_word_doc
from .models import DocQueries, IndexQueries
from django.templatetags.static import static

import os
from django.conf import settings
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent

from django.contrib.staticfiles.storage import staticfiles_storage

def main(request, team_slug):
    if request.user.is_authenticated:
        # return render(request, 'web/demo/demo.html')
        search_text = "__"
        print(request)
        # if request.method == 'POST' and 'load-docs' in request.POST:
        # if request.method == 'POST' and 'search-text' in request.POST:
        #     print('search-text')
        #     search_text = request.POST.get('search-text')

        #     # doc_text = read_word_doc(search_text)

        #     return render(request, 'web/demo/demo.html', 
        #                     {'es_files': 'filler',
        #                     'upload_msg': '_____'})

        # if request.method == 'POST' and len(request.FILES.getlist('load-docs'))>0 and 'search-text' in request.POST:
        #     search_text = request.POST.get('search-text')
        #     files_to_upload = request.FILES.getlist('load-docs')
        #     upload_counter = 0
        #     user = request.user.username
        #     for x in files_to_upload:
        #         upload_counter += 1
        #         upload_msg = 'Uploading document ' + str(upload_counter) + ' of ' + str(len(files_to_upload))
        #         print(upload_msg + "\t" + str(x))
        #         request.POST.get('upload_msg', upload_msg + '\t' + str(x))

        #         # doc_text_list = []
        #         for file in files_to_upload:
        #             raw_data = read_word_doc(file)
        #             analysis = interpret_text(search_text, raw_data)
        #             # doc_text_list.append(read_word_doc(file))
        #             print(analysis)
        #             doc = DocQueries(
        #                 USER = user,
        #                 DOC_NAME= file,
        #                 DOC_TEXT = raw_data,
        #                 QUERY = search_text,
        #                 GPT_RESPONSE = analysis['gpt_response'],
        #                 COMPLETION_TOKENS = analysis['completion_tokens'],
        #                 PROMPT_TOKENS = analysis['prompt_tokens'],
        #                 QUERY_DATE = datetime.now()
        #                 )
        #             doc.save()

        #     # df = DocQueries.objects.filter(USER=user).all().values(*values).distinct()
        #     queries = DocQueries.objects.filter(USER=user).all().distinct().order_by('-QUERY_DATE')
                    
        #     return render(request, 'web/demo/demo.html', 
        #                             {'queries': queries,
        #                             'upload_msg': 'File upload finished!!'})

        if request.method == 'POST' and 'search-text' in request.POST: #
            user = request.user.username

            # index_path = '/code/static/misc_data/gpt_index_testing_index.json'
            index_path = '/code/static/misc_data/gpt_index_justia_index.json'

            index = GPTSimpleVectorIndex.load_from_disk(index_path)

            search_text = request.POST.get('search-text')

            response = index.query(search_text)

            total_llm_token_usage = index.llm_predictor.last_token_usage
            total_embedding_token_usage = index.embed_model.last_token_usage

            doc = IndexQueries(
                USER = user,
                INDEX_NAME = os.path.basename(index_path),
                QUERY = search_text,
                GPT_RESPONSE = response,
                TOTAL_LLM_TOKEN_USAGE = total_llm_token_usage,
                TOTAL_EMBEDDING_TOKEN_USAGE = total_embedding_token_usage,
                QUERY_DATE = datetime.now()
            )
            doc.save()

            queries = IndexQueries.objects.filter(USER=user).all().distinct().order_by('QUERY_DATE')

            return render(request, 'web/demo/demo.html', 
                                    {'queries': queries,
                                    'upload_msg': 'File upload finished!!'})
    
        return render(request, 'web/demo/demo.html')
    else:
        return render(request, 'web/landing_page.html')


# @login_and_team_required
