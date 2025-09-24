import graphene
import graphql_jwt

import business.schema as business
import business.schema_task as task
import business.schema_module as module
import card.schema as card
import processflow.schema_process as process
import processflow.schema as processflow
import core.schema_message as message
import business.schema_contact as contact
import card.schema_bot as bot
import card.schema_voice as voice
import authtf.schema_user as user
import salon.schemas.salon as salon
import salon.schemas.category as salonCategory
import salon.schemas.floor_plan as salonFloorPlan
import salon.schemas.membership_type as salonMembershipType
import salon.schemas.beautician as salonBeautician
import salon.schemas.calendar as calendar
import salon.schemas.entity_type as entity_type
import salon.schemas.customer as salonCustomer
import salon.schemas.service as salonService
import salon.schemas.product as salonProduct
import salon.schemas.pos as salonPos
import salon.schemas.variant as salonVariant
import salon.schemas.session as salonSession
import salon.schemas.membership_service as salonMembershipService
import salon.schemas.setting as salonSetting
import salon.schemas.selectors as selectors
import salon.schemas.micro_tasks as micro_tasks
import salon.schemas.queue as queue
import salon.schemas.selectors_v1 as selectors_v1
import salon.schemas.selectors_v2 as selectors_v2
import authtf.schema_invitation as schema_invitation
import authtf.schema_login as schema_login
import authtf.schema_feedback as authtf_feeback
import salon.schemas.selectors_v3 as selectors_v3
import salon.schemas.ai_queue as ai_queue
import core.schema_google_sheet as schema_google_sheet
import agent.schema_agent_parameter as schema_agent_parameter
import agent.schema_ehr as schema_ehr
import agent.schema_agent_otp as schema_agent_otp
import ad.schemas.country as country
import ad.schemas.state as state
import ad.schemas.city as city
import ad.schemas.specialization as specialization
import ad.schemas.specialization_category as specialization_category
import ad.schemas.doctor as doctor
import ad.schemas.chat_history as chat_history
import ad.schemas.chat_history_category as chat_history_category
import ad.schemas.insurance_provider as insurance_provider
import ad.schemas.micro_tasks_v2 as ad_micro_tasks_v2
import ad.schemas.micro_tasks as ad_micro_tasks
import ad.schemas.patient_booking as patient_booking
import ad.schemas.user_chat_history as user_chat_history
import ad.schemas.notification as notification
import ad.schemas.language as doctor_language
import ad.schemas.populate_data as populated_data
import ad.schemas.provider_timeslot as provider_timeslot
import ad.schemas.patient_queue as patient_queue
import ad.schemas.gender as doctor_gender
import ad.schemas.ethnicity as doctor_ethnicity
import ad.schemas.lab as lab
import ad.schemas.referral as referral
import ad.schemas.chat_keywords as chat_keywords
import ad.schemas.clinic as clinic

class Query(
            entity_type.schema_entity_type.Query,
            calendar.schema_calendar.Query,
            user.schema_user.Query,
            business.schema.Query,
            task.schema_task.Query,
            module.schema_module.Query,
            card.schema.Query,
            process.schema_process.Query, processflow.schema.Query,
            message.schema_message.Query, contact.schema_contact.Query,
            bot.schema_bot.Query,
            voice.schema_voice.Query,
            salon.schema_salon.Query,
            salonCategory.schema_salon_category.Query,
            salonFloorPlan.schema_salon_floor_plan.Query,
            salonMembershipType.schema_salon_membership_type.Query,
            salonBeautician.schema_salon_beautician.Query,
            salonCustomer.schema_salon_customer.Query,
            salonService.schema_salon_service.Query,
            salonProduct.schema_salon_product.Query,
            salonPos.schema_salon_pos.Query,
            salonVariant.schema_salon_variant.Query,
            salonSession.schema_salon_session.Query,
            salonMembershipService.schema_salon_membership_service.Query,
            salonSetting.schema_salon_setting.Query,
            selectors.schema_selector.Query,
            queue.schema_salon_queue.Query,
            selectors_v1.schema_selector_v1.Query,
            selectors_v2.schema_selector_v2.Query,
            schema_invitation.schema_invitation.Query,
            schema_login.schema_login.Query,
            authtf_feeback.schema_feedback.Query,
            selectors_v3.schema_selector_v3.Query,
            ai_queue.schema_ai_queue.Query,
            schema_agent_parameter.schema_agent_parameter.Query,
            schema_ehr.schema_ehr.Query,
            schema_agent_otp.schema_agent_otp.Query,
            country.country_schema.Query,
            state.state_schema.Query,
            city.city_schema.Query,
            specialization.specialization_schema.Query,
            specialization_category.specialization_category_schema.Query,
            doctor.doctor_schema.Query,
            chat_history.chat_history_schema.Query,
            chat_history_category.chat_history_category_schema.Query,
            insurance_provider.insurance_provider_schema.Query,
            patient_booking.patient_booking_schema.Query,
            user_chat_history.user_chat_history_schema.Query,
            notification.notification_schema.Query,
            ad_micro_tasks.schema_ad_micro_tasks.Query,
            doctor_language.language_schema.Query,
            populated_data.populate_data_schema.Query,
            provider_timeslot.provider_timeslot_schema.Query,
            patient_queue.patient_queue_schema.Query,
            doctor_gender.gender_schema.Query,
            doctor_ethnicity.ethnicity_schema.Query,
            lab.lab_schema.Query,
            referral.referral_schema.Query,
            chat_keywords.chat_keyword_schema.Query,
            clinic.clinic_schema.Query,
            graphene.ObjectType):
    # Inherits all classes and methods from app-specific queries, so no need
    # to include additional code here.
    pass

class Mutation(
               calendar.schema_calendar.Mutation,
               user.schema_user.Mutation,
               business.schema.Mutation,
               task.schema_task.Mutation,
               module.schema_module.Mutation,
               card.schema.Mutation,
               process.schema_process.Mutation, processflow.schema.Mutation,
               message.schema_message.Mutation, contact.schema_contact.Mutation,
               salonCategory.schema_salon_category.Mutation,
               salonFloorPlan.schema_salon_floor_plan.Mutation,
               salonMembershipType.schema_salon_membership_type.Mutation,
               salonBeautician.schema_salon_beautician.Mutation,
               salonCustomer.schema_salon_customer.Mutation,
               salonService.schema_salon_service.Mutation,
               salonProduct.schema_salon_product.Mutation,
               salonPos.schema_salon_pos.Mutation,
               salonVariant.schema_salon_variant.Mutation,
               salonSession.schema_salon_session.Mutation,
               salonMembershipService.schema_salon_membership_service.Mutation,
               salonSetting.schema_salon_setting.Mutation,
               micro_tasks.schema_micro_tasks.Mutation,
               queue.schema_salon_queue.Mutation,
               schema_invitation.schema_invitation.Mutation,
               schema_login.schema_login.Mutation,
               authtf_feeback.schema_feedback.Mutation,
               ai_queue.schema_ai_queue.Mutation,
               schema_google_sheet.schema_google_sheet.Mutation,
               schema_agent_parameter.schema_agent_parameter.Mutation,
               schema_ehr.schema_ehr.Mutation,
               schema_agent_otp.schema_agent_otp.Mutation,
               country.country_schema.Mutation,
               state.state_schema.Mutation,
               city.city_schema.Mutation,
               specialization.specialization_schema.Mutation,
               specialization_category.specialization_category_schema.Mutation,
               chat_history.chat_history_schema.Mutation,
               chat_history_category.chat_history_category_schema.Mutation,
               insurance_provider.insurance_provider_schema.Mutation,
               ad_micro_tasks_v2.schema_ad_micro_tasks_v2.Mutation,
               patient_booking.patient_booking_schema.Mutation,
               user_chat_history.user_chat_history_schema.Mutation,
               notification.notification_schema.Mutation,
               ad_micro_tasks.schema_ad_micro_tasks.Mutation,
               doctor_language.language_schema.Mutation,
               provider_timeslot.provider_timeslot_schema.Mutation,
               patient_queue.patient_queue_schema.Mutation,
               doctor_gender.gender_schema.Mutation,
               doctor_ethnicity.ethnicity_schema.Mutation,
               lab.lab_schema.Mutation,
               referral.referral_schema.Mutation,
               chat_keywords.chat_keyword_schema.Mutation,
               clinic.clinic_schema.Mutation,
               graphene.ObjectType):
    # Inherits all classes and methods from app-specific mutations, so no need
    # to include additional code here.
    pass

# class Subscription(pubsub.pubsub_schema.Subscription,
#                graphene.ObjectType):
#     # Inherits all classes and methods from app-specific mutations, so no need
#     # to include additional code here.
#     pass

schema = graphene.Schema(query=Query, mutation=Mutation
                        #  subscription=Subscription
                        )