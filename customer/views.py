from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

import inverite
import logging


@xframe_options_exempt
@csrf_exempt
def index(request):
    return render(request, "customer/index.html")


@xframe_options_exempt
@csrf_exempt
def request(request, guid=""):
    posted_guid = request.POST.get("guid", None)
    if posted_guid:
        guid = posted_guid
    if guid:
        return redirect('choose_bank', guid=guid)
    else:
        return render(request, "customer/request.html", {})


@xframe_options_exempt
@csrf_exempt
def choose_bank(request, guid):
    bankID = request.POST.get("bankID", "")
    logging.error("ip might be %s" % get_ip(request))
    if all([guid, bankID]):
        return redirect('bank_form', guid=guid, bankID=bankID)
    try:
        banks = inverite.fetch_banks(guid)
    except Exception as e:
        messages.error(request, e)

    if messages.get_messages(request):
        return showerror(request)
    else:
        return render(request, "customer/choose_bank.html", {
            "banks": banks,
            "guid": guid
        })


@xframe_options_exempt
@csrf_exempt
def bank_form(request, guid, bankID, job_id=None):
    status = {"status": "", "message": ""}
    try:
        fields = inverite.fetch_bankform(bankID)
        if job_id:
            status = inverite.fetch_session_status(job_id)
    except Exception as e:
        messages.error(request, e)

    logging.error(status)
    if messages.get_messages(request):
        return showerror(request)
    else:
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        branch = request.POST.get("branch", "")
        ip = get_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT')
        logging.error(user_agent)
        if all([username, password]):
            logging.error("have username and password")
            try:
                result = inverite.session_start(
                    guid, bankID, username, password, branch, ip, user_agent
                )
                logging.error("result is %s " % result)
                if "errors" in result:
                    logging.error("errors in result")
                    if "validation_error" in result["errors"]:
                        return render(request, "customer/bank_form.html", {
                            "guid": guid,
                            "bankID": bankID,
                            "fields": fields,
                            "form_errors": result["form_errors"]
                        })
                    else:
                        return render(request, "customer/bank_form.html", {
                            "guid": guid,
                            "bankID": bankID,
                            "fields": fields,
                            "errors": result["errors"]
                        })
                elif "job_id" in result:
                    return redirect('session_status',
                                    guid=guid,
                                    bankID=bankID,
                                    job_id=result["job_id"])
                else:
                    logging.error("result was no good: %s" % result)
            except Exception as e:
                messages.error(request, e)
                return showerror(request)
        else:
            return render(request, "customer/bank_form.html",
                          {"guid": guid, "fields": fields,
                           "status": status.get("status", ""),
                           "message": status.get("message", ""),
                           "bankID": bankID}
                          )


@xframe_options_exempt
@csrf_exempt
def session_status_json(request, guid, bankID, job_id):
    try:
        logging.error("session_status_refresh sending hit for %s" % job_id)
        result = inverite.fetch_session_status(job_id)
        logging.error("session_status_refresh result is  %s" % result)
    except Exception as e:
        result = {'errors': ['trapped api error']}
    return JsonResponse(result)


@xframe_options_exempt
@csrf_exempt
def session_status(request, guid, bankID, job_id):
    return render(request, "customer/wait.html",
                  {"guid": guid, "bankID": bankID,
                   "job_id": job_id, "progress": 0})


@xframe_options_exempt
@csrf_exempt
def session_status_refresh(request, guid, bankID, job_id):
    if all([guid, bankID, job_id]):
        try:
            logging.error("session_status_refresh sending hit for %s" % job_id)
            result = inverite.fetch_session_status(job_id)
            logging.error("session_status_refresh result is  %s" % result)
        except ValueError as e:
            messages.error(request, e)
            return showerror(request)
        except Exception as e:
            messages.error(request, e)
            return showerror(request)

        status = result.get('status', '')
        if status in ["error", "challengefail", "authfail",
                      "bank_unavailable", "blocked",
                      "challengetimeout", "login_required"]:
            return redirect('bank_form_status_message',
                            guid=guid,
                            bankID=bankID,
                            status=status,
                            message=result.get('message', 'none'))
        elif status == "need_input":
            return render(request, "customer/challenge_response.html",
                          {"guid": guid, "bankID": bankID,
                           "job_id": job_id,
                           "challenge": result.get("challenge", "")})
        elif status == "need_dropdown_input":
            return render(request, "customer/challenge_response_dropdown.html",
                          {"guid": guid, "bankID": bankID,
                           "job_id": job_id,
                           "challenge": result.get("challenge", ""),
                           "options": result.get("options", "")})
        elif status == "need_image_coordinate_input":
            return render(request, "customer/challenge_response_image.html",
                          {"guid": guid, "bankID": bankID,
                           "job_id": job_id,
                           "image": result.get("image", "")})
        elif status in ["working", "unknown"]:
            if "progress" not in result:
                result["progress"] = "0"
            return render(request, "customer/wait.html",
                          {"guid": guid, "bankID": bankID,
                           "job_id": job_id, "progress": result["progress"]})
        elif status == "success":
            return render(request, "customer/success.html",
                          {"guid": guid, "bankID": bankID, "job_id": job_id})
        else:
            messages.error(request, "Unknown status; %s" % status)
            return showerror(request)


@xframe_options_exempt
def challenge_response_image(request, guid, bankID, job_id):
    try:
        result = inverite.fetch_session_status(job_id)
    except Exception as e:
        messages.error(request, e)
        return showerror(request)

    return render(request, "customer/challenge_response_image.html",
                  {"guid": guid, "bankID": bankID,
                   "job_id": job_id,
                   "challenge": result.get("challenge", "")})


@xframe_options_exempt
def challenge_response_dropdown(request, guid, bankID, job_id):
    try:
        result = inverite.fetch_session_status(job_id)
    except Exception as e:
        messages.error(request, e)
        return showerror(request)

    return render(request, "customer/challenge_response_dropdown.html",
                  {"guid": guid, "bankID": bankID,
                   "job_id": job_id,
                   "challenge": result.get("challenge", ""),
                   "options": result.get("options", "")})


@xframe_options_exempt
def success(request, guid, bankID, job_id):
    return render(request, "customer/success.html",
                  {"guid": guid, "bankID": bankID,
                   "job_id": job_id})


@xframe_options_exempt
def challenge_response(request, guid, bankID, job_id):
    try:
        result = inverite.fetch_session_status(job_id)
    except Exception as e:
        messages.error(request, e)
        return showerror(request)
    return render(request, "customer/challenge_response.html",
                  {"guid": guid, "bankID": bankID,
                   "job_id": job_id,
                   "challenge": result.get("challenge", "")})


@xframe_options_exempt
@csrf_exempt
def provide_challenge_response(request, guid, bankID, job_id):
    challenge_response = request.POST.get("challenge_response", "")
    if challenge_response:
        logging.error("add some functionality")
        challenge_result = inverite.provide_challenge_response(
            job_id, challenge_response)
        if "errors" in challenge_result:
            try:
                fields = inverite.fetch_bankform(bankID)
            except Exception as e:
                messages.error(request, e)
            return render(request, "customer/bank_form.html",
                          {"guid": guid, "fields": fields,
                           "errors": challenge_result["errors"]})
        else:
            return redirect(session_status,
                            guid=guid,
                            bankID=bankID,
                            job_id=job_id)
    else:
        return redirect(session_status,
                        guid=guid,
                        bankID=bankID,
                        job_id=job_id)


@xframe_options_exempt
@csrf_exempt
def showerror(request, message=None, source=None):
    return render(request, "customer/error.html")


@xframe_options_exempt
@csrf_exempt
def wait(request):
    return render(request, "customer/wait.html")


def get_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_REAL_IP')
    if x_forwarded_for:
        logging.error("x-forwarded-for")
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
