from http.server import HTTPServer, BaseHTTPRequestHandler
from services.telegram_api_utils import TelegramApiUtils
from datetime import datetime, timedelta, timezone
import json
import re


class TrelloActivityHandler(BaseHTTPRequestHandler):

    MESSAGE_PATTERN_FOR_UPDATED_OR_TRANSFERED_TICKETS = "'<b>{issue}</b>' issue was {action}. \
    \n\t\t" + u'\U0000270F' + " Previous {eventValue}: <s><i>{before}</i></s> \
    \n\t\t" + u'\U0001F4CC' + " New one: <u><i>{after}</i></u> \
    \n---\
    \nChange was made by \"<u><i>{initiatorFullName}</i></u>\"\n" + u'\U000027A1' + "\
    <a href=\"https://trello.com/c/{issueShortLink}\">click here to see more</a>"

    MESSAGE_PATTERN_FOR_COMMENTED_ON_TICKETS = "'<b>{issue}</b>' issue was commented with: \
    \n\t\t" + u'\U0001F4AC' + " <i>{comment}</i> \
    \n---\
    \nBy \"<u><i>{initiatorFullName}</i></u>\"\n" + u'\U000027A1' + "\
    <a href=\"https://trello.com/c/{issueShortLink}\">click here to see more</a>"

    MESSAGE_PATTERN_FOR_DONE_CHECK_IN_CHECK_LIST = "Element of check-list at issue '<b>{issue}</b>' was marked as <u><i>DONE</i></u>:\
    \n\t\t" + u'\U00002705' + " <i>{checkListElement}</i> \
    \n---\
    \nBy \"<u><i>{initiatorFullName}</i></u>\"\n" + u'\U000027A1' + "\
    <a href=\"https://trello.com/c/{issueShortLink}\">click here to see more</a>"

    MESSAGE_PATTERN_FOR_UNDONE_CHECK_IN_CHECK_LIST = "Element of check-list at issue '<b>{issue}</b>' was marked as <u><i>UNDONE</i></u>:\
    \n\t\t" + u'\U0000274C' + " <i>{checkListElement}</i>\
    \n---\
    \nBy \"<u><i>{initiatorFullName}</i></u>\"\n" + u'\U000027A1' + "\
    <a href=\"https://trello.com/c/{issueShortLink}\">click here to see more</a>"

    MESSAGE_PATTERN_FROM_ADDED_ATTACHMENTS = "'<b>{issue}</b>' issue has been updated by adding an <a href=\"{attachmentPreviewLink}\">attachment</a>\
    \n---\
    \nBy \"<u><i>{initiatorFullName}</i></u>\"\n" + u'\U000027A1' + "\
    <a href=\"https://trello.com/c/{issueShortLink}\">click here to see more</a>"

    MESSAGE_PATTERN_FOR_CUD_CHECK_LIST_ELEMENTS = "The element of checklist at issue '<b>{issue}</b>' was <i>{action}</i>:\
    \n\t\t{emojiAction} <i>{checkListElement}</i> \
    \n---\
    \nBy \"<u><i>{initiatorFullName}</i></u>\"\n" + u'\U000027A1' + "\
    <a href=\"https://trello.com/c/{issueShortLink}\">click here to see more</a>"

    MESSAGE_PATTERN_FOR_RENAMED_ELEMENTS_OF_CHECK_LISTS = "The element of checklist at issue '<b>{issue}</b>' was renamed. \
    \n\t\t" + u'\U0000270F' + " Previous {eventValue}: <s><i>{before}</i></s> \
    \n\t\t" + u'\U0001F4CC' + " New one: <u><i>{after}</i></u> \
    \n---\
    \nChange was made by \"<u><i>{initiatorFullName}</i></u>\"\n" + u'\U000027A1' + "\
    <a href=\"https://trello.com/c/{issueShortLink}\">click here to see more</a>"

    MESSAGE_PATTERN_FOR_ASSIGNED_OR_UNASSIGNED_ON_TICKETS = "You were {action} issue '<b>{issue}</b>'.\
    \n---\
    \nBy \"<u><i>{initiatorFullName}</i></u>\"\n" + u'\U000027A1' + "\
    <a href=\"https://trello.com/c/{issueShortLink}\">click here to see more</a>"

    MESSAGE_PATTERN_TICKET_WAS_CREATED_OR_DELETED = u'\U0001F5D2' + " Issue '<b>{issue}</b>' was {action}.\
    \n---\
    \nBy \"<u><i>{initiatorFullName}</i></u>\"\n" + u'\U000027A1' + "\
    <a href=\"https://trello.com/c/{issueShortLink}\">click here to see more</a>"

    def do_HEAD(self):
        print("[INFO] Received HEAD request on {path}".format(path = self.path))

        if self.path[1:] != self.server.trello_secured_endpoint:
            self.send_response(401)
            self.send_header('Content-type','text/html')
            self.end_headers()
            return 

        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        return 

    def do_GET(self):
        print("[INFO] Received GET request on {path}".format(path = self.path))

        if self.path[1:] != self.server.trello_secured_endpoint:
            self.send_response(401)
            self.send_header('Content-type','text/html')
            self.end_headers()
            return 

        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        return

    def do_POST(self):
        print("[INFO] Received POST request on {path}".format(path = self.path))

        if self.path[1:] != self.server.trello_secured_endpoint:
            self.send_response(401)
            self.send_header('Content-type','text/html')
            self.end_headers()
            return 

        trello_dashboard_update_info = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        print("[DEBUG] Received the next JSON payload: \n{}".format(json.dumps(trello_dashboard_update_info, indent = 2)))
        
        received_action_type = trello_dashboard_update_info['action']['type']
        received_action_subtype = trello_dashboard_update_info['action']['display']['translationKey']
        print("[INFO] Received action from trello: {actionType} _ {actionSubtype}".format(
            actionType = received_action_type, actionSubtype = received_action_subtype
        ))

        action_initiator_fullname = trello_dashboard_update_info['action']['memberCreator']['fullName']
        action_initiator_username = trello_dashboard_update_info['action']['memberCreator']['username']

        telegramApiUtils = TelegramApiUtils(self.server.telegram_token)
        result_message = ''
        
        card_id = ''
        try: card_id = trello_dashboard_update_info['action']['data']['card']['id']
        except: print("[ERROR] An exception occurred: can't get card identifier from the received update")
        if received_action_type == 'updateCard':
            action_card_shortlink = trello_dashboard_update_info['action']['data']['card']['shortLink']
            if received_action_subtype == 'action_move_card_from_list_to_list':

                result_object = {'card_title': '', 'from': '', 'to': ''}
                result_object['card_title'] = trello_dashboard_update_info['action']['display']['entities']['card']['text']
                result_object['from'] = trello_dashboard_update_info['action']['display']['entities']['listBefore']['text']
                result_object['to'] = trello_dashboard_update_info['action']['display']['entities']['listAfter']['text']

                # result_markers = ''
                # for v in trello_dashboard_update_info['model']['labelNames'].items():
                #     if v != '': result_markers = result_markers + ',' + str(v)
                # result_markers = result_markers[1:-1]

                if telegramApiUtils.get_me():
                    print('[INFO] Connection with telegram bot has been installed successfully')
                else:
                    print('[ERROR] Connection with telegram bot has not been installed')
                    exit()

                result_message = TrelloActivityHandler.MESSAGE_PATTERN_FOR_UPDATED_OR_TRANSFERED_TICKETS.format(
                    issue = result_object['card_title'],
                    action = "moved",
                    eventValue = "column",
                    before = result_object['from'],
                    after = result_object['to'],
                    initiatorFullName = action_initiator_fullname,
                    issueShortLink = action_card_shortlink
                )
            if received_action_subtype == 'action_changed_description_of_card':
                result_message = TrelloActivityHandler.MESSAGE_PATTERN_FOR_UPDATED_OR_TRANSFERED_TICKETS.format(
                    issue = trello_dashboard_update_info['action']['data']['card']['name'],
                    action = "updated (description)",
                    eventValue = "description",
                    before = trello_dashboard_update_info['action']['data']['old']['desc'],
                    after = trello_dashboard_update_info['action']['data']['card']['desc'],
                    initiatorFullName = action_initiator_fullname,
                    issueShortLink = action_card_shortlink
                )
            if received_action_subtype == 'action_renamed_card':
                result_message = TrelloActivityHandler.MESSAGE_PATTERN_FOR_UPDATED_OR_TRANSFERED_TICKETS.format(
                    issue = trello_dashboard_update_info['action']['data']['card']['name'],
                    action = "renamed",
                    eventValue = "title",
                    before = trello_dashboard_update_info['action']['data']['old']['name'],
                    after = trello_dashboard_update_info['action']['data']['card']['name'],
                    initiatorFullName = action_initiator_fullname,
                    issueShortLink = action_card_shortlink
                )
            if received_action_subtype == 'action_added_a_due_date' or received_action_subtype == 'action_changed_a_due_date':
                # ticket shoul be moved to the corresponding column
                self.server.trello_api_utils.transfer_ticket_to_corresponding_column_by_its_due_date(card_id)

        ### handle complete/incomplete stats of check-list elements
        if received_action_type == 'updateCheckItemStateOnCard':
            # print(trello_dashboard_update_info['action']['data']['checklist']['name'])
            action_card_shortlink = trello_dashboard_update_info['action']['data']['card']['shortLink']
            if received_action_subtype == 'action_completed_checkitem':
                result_message = TrelloActivityHandler.MESSAGE_PATTERN_FOR_DONE_CHECK_IN_CHECK_LIST.format(
                    issue = trello_dashboard_update_info['action']['data']['card']['name'],
                    checkListElement = trello_dashboard_update_info['action']['data']['checkItem']['name'],
                    initiatorFullName = action_initiator_fullname,
                    issueShortLink = action_card_shortlink
                )
            elif received_action_subtype == 'action_marked_checkitem_incomplete':
                result_message = TrelloActivityHandler.MESSAGE_PATTERN_FOR_UNDONE_CHECK_IN_CHECK_LIST.format(
                    issue = trello_dashboard_update_info['action']['data']['card']['name'],
                    checkListElement = trello_dashboard_update_info['action']['data']['checkItem']['name'],
                    initiatorFullName = action_initiator_fullname,
                    issueShortLink = action_card_shortlink
                )
        
        ### actions of check-list elements
        if received_action_type == 'createCheckItem':
            action_card_shortlink = trello_dashboard_update_info['action']['data']['card']['shortLink']
            card_title = trello_dashboard_update_info['action']['data']['card']['name']
            result_message = TrelloActivityHandler.MESSAGE_PATTERN_FOR_CUD_CHECK_LIST_ELEMENTS.format(
                issue = card_title,
                action = "created",
                emojiAction = u'\U00002795',
                checkListElement = trello_dashboard_update_info['action']['data']['checkItem']['name'],
                initiatorFullName = action_initiator_fullname,
                issueShortLink = action_card_shortlink
            )
        if received_action_type == 'deleteCheckItem':
            action_card_shortlink = trello_dashboard_update_info['action']['data']['card']['shortLink']
            card_title = trello_dashboard_update_info['action']['data']['card']['name']
            result_message = TrelloActivityHandler.MESSAGE_PATTERN_FOR_CUD_CHECK_LIST_ELEMENTS.format(
                issue = card_title,
                action = "removed",
                emojiAction = u'\U00002796',
                checkListElement = trello_dashboard_update_info['action']['data']['checkItem']['name'],
                initiatorFullName = action_initiator_fullname,
                issueShortLink = action_card_shortlink
            )
        if received_action_type == 'updateCheckItem' and received_action_subtype == 'action_renamed_checkitem':
            action_card_shortlink = trello_dashboard_update_info['action']['data']['card']['shortLink']
            card_title = trello_dashboard_update_info['action']['data']['card']['name']
            result_message = TrelloActivityHandler.MESSAGE_PATTERN_FOR_RENAMED_ELEMENTS_OF_CHECK_LISTS.format(
                issue = card_title,
                checkListElement = trello_dashboard_update_info['action']['data']['checkItem']['name'],
                eventValue = 'content',
                before = trello_dashboard_update_info['action']['data']['old']['name'],
                after = trello_dashboard_update_info['action']['data']['checkItem']['name'],
                initiatorFullName = action_initiator_fullname,
                issueShortLink = action_card_shortlink
            )

        ### comments on the cards
        if received_action_type == 'commentCard' and received_action_subtype  == 'action_comment_on_card':
            action_card_shortlink = trello_dashboard_update_info['action']['data']['card']['shortLink']
            card_title = trello_dashboard_update_info['action']['data']['card']['name']
            result_message = TrelloActivityHandler.MESSAGE_PATTERN_FOR_COMMENTED_ON_TICKETS.format(
                issue = card_title,
                comment = trello_dashboard_update_info['action']['data']['text'],
                initiatorFullName = action_initiator_fullname,
                issueShortLink = action_card_shortlink
            )

        ### card attachments
        if received_action_type == 'addAttachmentToCard' and received_action_subtype  == 'action_add_attachment_to_card':
            action_card_shortlink = trello_dashboard_update_info['action']['data']['card']['shortLink']
            card_title = trello_dashboard_update_info['action']['data']['card']['name']
            result_message = TrelloActivityHandler.MESSAGE_PATTERN_FROM_ADDED_ATTACHMENTS.format(
                issue = card_title,
                attachmentPreviewLink = trello_dashboard_update_info['action']['data']['attachment']['previewUrl'],
                initiatorFullName = action_initiator_fullname,
                issueShortLink = action_card_shortlink
            )

        ### actions with un/assigned members on the cards
        if received_action_type == 'addMemberToCard' or received_action_type == 'removeMemberFromCard':
            action_card_shortlink = trello_dashboard_update_info['action']['data']['card']['shortLink']
            card_title = trello_dashboard_update_info['action']['data']['card']['name']
            if received_action_subtype == 'action_added_member_to_card':
                result_message = TrelloActivityHandler.MESSAGE_PATTERN_FOR_ASSIGNED_OR_UNASSIGNED_ON_TICKETS.format(
                    action = u'\U0000270C' + ' <u><i>assigned</i></u> to the',
                    issue = card_title,
                    initiatorFullName = action_initiator_fullname,
                    issueShortLink = action_card_shortlink
                )
            if received_action_subtype == 'action_removed_member_from_card':
                result_message = TrelloActivityHandler.MESSAGE_PATTERN_FOR_ASSIGNED_OR_UNASSIGNED_ON_TICKETS.format(
                    action = u'\U0001F91E' + ' <u><i>unassigned</i></u> from the',
                    issue = card_title,
                    initiatorFullName = action_initiator_fullname,
                    issueShortLink = action_card_shortlink
                )
            member_id = trello_dashboard_update_info['action']['data']['idMember']
            member_username = self.server.trello_api_utils.getMemberById(member_id)['username']
            member_telegram_trello_assignment = self.server.mongodb_utils.findUserTelegramTrelloAssignmentByTrelloUsername(
                member_username
            )
            if member_telegram_trello_assignment != None:
                telegramApiUtils.send_message(member_telegram_trello_assignment['telegram_chat_id'], result_message)
            else:
                print("[DEBUG] Assignment between trello username and telegram chat id has not been found. Expected username is = {}".format(
                    member_username
                ))
            # should be empty because we have already sent necessary message and we need to answer to webhook with 200 OK
            result_message = ''
        
        ### action for create or archive tickets
        if received_action_type == 'createCard' or (received_action_type == 'updateCard' and received_action_subtype == 'action_archived_card'):

            action_card_shortlink = trello_dashboard_update_info['action']['data']['card']['shortLink']
            card_title = trello_dashboard_update_info['action']['data']['card']['name']
            card_action = ''
            if received_action_subtype == 'action_archived_card':
                card_action = 'archived'
            if received_action_subtype == 'action_create_card':
                card_action = 'created'
            result_message = TrelloActivityHandler.MESSAGE_PATTERN_TICKET_WAS_CREATED_OR_DELETED.format(
                issue = card_title,
                action = u'\U0001F9E0' + ' <u><i>{}</i></u>'.format(card_action),
                initiatorFullName = action_initiator_fullname,
                issueShortLink = action_card_shortlink
            )

        # send result message after result_message created
        if result_message:
            # get card members
            card_members_usernames = []
            for member_id in self.server.trello_api_utils.getCardById(card_id)['idMembers']:
                card_members_usernames.append(self.server.trello_api_utils.getMemberById(member_id)['username'])
            # notify users which subscribed for ALL changes
            subscribers_for_all = self.server.mongodb_utils.findTrellloSubscribersByTheirSubscription(['ALL'])
            for subscriber_for_all in subscribers_for_all:
                if action_initiator_username != subscriber_for_all['trello_username']:
                    telegramApiUtils.send_message(subscriber_for_all['telegram_chat_id'], result_message)
            # notify specific subscribers
            for card_member_username in card_members_usernames:
                subscribers_for_specific_changes = self.server.mongodb_utils.findTrellloSubscribersByTheirSubscription([card_member_username])
                for subscriber_for_specific_subscription in subscribers_for_specific_changes:
                    if action_initiator_username != subscriber_for_specific_subscription['trello_username']:
                        telegramApiUtils.send_message(subscriber_for_specific_subscription['telegram_chat_id'], result_message)

        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        return

    def getUsernamesOfTicketAssigners(self, card_id):
        for memberId in self.server.trello_api_utils.getCardById(card_id)['idMembers']:
            print(self.server.trello_api_utils.getMemberById(memberId)['username'])