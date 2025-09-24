import graphene
from graphene_django import DjangoObjectType
from django.db import models
import json
from salon.models import *
from authtf.models import User
from organization.models import Organization
from django.db import transaction
import datetime
from django.conf import settings


class DataLoadModel(models.Model):
    status = models.TextField(blank=True)
    context = models.TextField(blank=True)

    class Meta:
        managed = False

class DataLoadModelType(DjangoObjectType):
  class Meta:
    model = DataLoadModel
    fields = ("status", "context")

class Query(graphene.ObjectType):
  salon_data_load = graphene.Field(DataLoadModelType,
                        commandIn=graphene.String())

  def getOrganization(self):
    return Organization.objects.get(pk=settings.TEST_ORGANIZATION)

  def loadEntityTypes(self, org):
    EntityType.objects.all().delete()
    et_service = EntityType(title = "Service", organization=org)
    et_service.save()
    et_cp = EntityType(title = "Consumable Products", organization=org)
    et_cp.save()
    et_sp = EntityType(title = "Storable Products", organization=org)
    et_sp.save()
    et_pos = EntityType(title = "Point of Sales", organization=org)
    et_pos.save()
    print("--- loadEntityTypes ---")
    return {et_service, et_cp, et_sp, et_pos}

  def loadCategory(self, et_service, et_cp, org):
    Category.objects.all().delete()
    ct_fs = Category(title="Facial & Skin Care", entity_type=et_service, organization=org)
    ct_fs.save()
    ct_hb = Category(title="Hair & Beard Styling", entity_type=et_service, organization=org)
    ct_hb.save()
    ct_hc = Category(title="Hair Color Services", entity_type=et_service, organization=org)
    ct_hc.save()
    ct_mk = Category(title="Makeup", entity_type=et_service, organization=org)
    ct_mk.save()
    ct_ms = Category(title="Massage", entity_type=et_service, organization=org)
    ct_ms.save()
    ct_rt = Category(title="Retail", entity_type=et_cp, organization=org)
    ct_rt.save()
    print("--- loadCategory ---")
    return {ct_fs, ct_hb, ct_hc, ct_mk, ct_ms, ct_rt}

  def loadBeautician(self, email, first_name, last_name, phone, org):
    User.objects.filter(email = email).delete()
    transaction.commit()
    usr_ = User(email = email, first_name = first_name,
                    last_name= last_name,
                    password_reset_code = None)
    usr_.set_password("12345678")
    usr_.save()
    btc_ = Beautician(linked_user = usr_, phone = phone, organization=org)
    btc_.save()
    print("--- loadBeautician ---")
    return btc_

  def loadSalonCustomers(self, et_service, et_cp, org):
    CustomerSalon.objects.all().delete()
    cs_olivia = CustomerSalon(first_name = "Olivia", last_name = "Scott",
                              email = "olivia_scott@tfax.com", phone = "1234567890", organization=org)
    cs_olivia.save()
    cs_emma = CustomerSalon(first_name = "Emma", last_name = "Lee",
                              email = "emma_lee@tfax.com", phone = "1234567890", organization=org)
    cs_emma.save()
    cs_thomas = CustomerSalon(first_name = "Thomas", last_name = "Vance",
                              email = "thomas_vance@tfax.com", phone = "1234567890", organization=org)
    cs_thomas.save()
    cs_paul = CustomerSalon(first_name = "Paul", last_name = "Forest",
                              email = "paul_forest@tfax.com", phone = "1234567890", organization=org)
    cs_paul.save()
    cs_peter = CustomerSalon(first_name = "Peter", last_name = "Mathhew",
                              email = "peter_matthew@tfax.com", phone = "1234567890", organization=org)
    cs_peter.save()
    print("--- loadSalonCustomers ---")
    return {cs_olivia, cs_emma, cs_thomas, cs_paul, cs_peter}


  def loadFloorplan(self, org):
    FloorPlan.objects.all().delete()
    floor_men = FloorPlan(title = "Men", position = 1, organization=org)
    floor_men.save()
    floor_women = FloorPlan(title = "Women", position = 2, organization=org)
    floor_women.save()
    floor_kids = FloorPlan(title = "Kids", position = 3, organization=org)
    floor_kids.save()
    print("--- loadFloorplan ---")
    return {floor_men, floor_women, floor_kids}

  def loadPos(self, floor_men, floor_women, floor_kids, et_pos, org):
    Pos.objects.all().delete()
    pos_m1 = Pos(title = "POSM1", entity_type = et_pos, floorplan = floor_men, position = 1, organization=org)
    pos_m1.save()
    pos_m2 = Pos(title = "POSM2", entity_type = et_pos, floorplan = floor_men, position = 1, organization=org)
    pos_m2.save()
    pos_m3 = Pos(title = "POSM3", entity_type = et_pos, floorplan = floor_men, position = 1, organization=org)
    pos_m3.save()
    pos_m4 = Pos(title = "POSM4", entity_type = et_pos, floorplan = floor_men, position = 1, organization=org)
    pos_m4.save()
    pos_w1 = Pos(title = "POSW1", entity_type = et_pos, floorplan = floor_women, position = 1, organization=org)
    pos_w1.save()
    pos_w2 = Pos(title = "POSW2", entity_type = et_pos, floorplan = floor_women, position = 1, organization=org)
    pos_w2.save()
    pos_w3 = Pos(title = "POSW3", entity_type = et_pos, floorplan = floor_women, position = 1, organization=org)
    pos_w3.save()
    pos_k1 = Pos(title = "POSK1", entity_type = et_pos, floorplan = floor_kids, position = 1, organization=org)
    pos_k1.save()
    pos_k2 = Pos(title = "POSK2", entity_type = et_pos, floorplan = floor_kids, position = 1, organization=org)
    pos_k2.save()
    pos_k3 = Pos(title = "POSK3", entity_type = et_pos, floorplan = floor_kids, position = 1, organization=org)
    pos_k3.save()
    pos_k4 = Pos(title = "POSK4", entity_type = et_pos, floorplan = floor_kids, position = 1, organization=org)
    pos_k4.save()
    pos_k5 = Pos(title = "POSK5", entity_type = et_pos, floorplan = floor_kids, position = 1, organization=org)
    pos_k5.save()
    print("--- loadPos ---")
    return {pos_m1, pos_m2, pos_m3, pos_m4, pos_w1, pos_w2, pos_w3, pos_k1, pos_k2, pos_k3, pos_k4, pos_k5}


  def loadMembershipType(self, org):
    MembershipType.objects.all().delete()
    mtype_1 = MembershipType(title = "Basic Spa Membership", fee = 100.0, billing_period = 1, organization=org)
    mtype_1.save()
    mtype_2 = MembershipType(title = "Basic Mani-Padi Membership", fee = 250.0, billing_period = 1, organization=org)
    mtype_2.save()
    mtype_3 = MembershipType(title = "Total Treatment Membership", fee = 300.0, billing_period = 1, organization=org)
    mtype_3.save()
    print("--- loadMembershipType ---")
    return {mtype_1, mtype_2, mtype_3}


  def loadProducts(self, ct_rt, org):
    Product.objects.all().delete()
    p1 = Product(title = "AG balance 355ml", cost_price = 100.0, sales_price = 115.0, category = ct_rt, organization=org)
    p1.save()
    p2 = Product(title = "LP Silver Shampoo 300ml", cost_price = 125.50,sales_price = 144.50, category = ct_rt, organization=org)
    p2.save()
    p3 = Product(title = "LP TA air fix 400ml", cost_price = 230.75, sales_price = 250.75, category = ct_rt, organization=org)
    p3.save()
    p4 = Product(title = "PO color fanatic 30ml", cost_price = 75.30, sales_price = 95.30, category = ct_rt, organization=org)
    p4.save()
    p5 = Product(title = "Shu BB serum fine 150m", cost_price = 115.0, sales_price = 127.0, category = ct_rt, organization=org)
    p5.save()
    p6 = Product(title = "Shu Satin design 250ml", cost_price = 315.40, sales_price = 365.40, category = ct_rt, organization=org)
    p6.save()
    p7 = Product(title = "Shu Volume Maker 2g", cost_price = 44.20, sales_price = 64.20, category = ct_rt, organization=org)
    p7.save()
    print("--- loadProducts ---")
    return {p1, p2, p3, p4, p5, p6, p7}


  def loadServices(self, ct_fs, ct_hb, ct_hc, ct_mk, ct_ms, org):
    Service.objects.all().delete()
    s1 = Service(title = "Haircut",
                 code = "HC-001",
                 cost_price = 100.0, sales_price = 115.0, category = ct_hc, organization=org)
    s1.save()
    s2 = Service(title = "Nails",
                 code = "HC-002", cost_price = 125.50,sales_price = 144.50, category = ct_mk, organization=org)
    s2.save()
    s3 = Service(title = "Massage",
                 code = "HC-003", cost_price = 230.75, sales_price = 250.75, category = ct_ms, organization=org)
    s3.save()
    s4 = Service(title = "Spa",
                 code = "HC-004", cost_price = 75.30, sales_price = 95.30, category = ct_ms, organization=org)
    s4.save()
    s5 = Service(title = "Color & Styling",
                 code = "HC-005", cost_price = 115.0, sales_price = 127.0, category = ct_mk, organization=org)
    s5.save()
    print("--- loadServices ---")
    return {s1, s2, s3, s4, s5}


  def loadVariants(self, s1, s2, s3, s4, s5, org):
    Variant.objects.all().delete()
    v1 = Variant(title = "Beard Trim",
                 cost_price = 100.0, sales_price = 115.0,
                 entity_type = s1.category.entity_type,
                 entity_id = s1.id, organization=org)
    v1.save()
    v2 = Variant(title = "Men's Haircut",
                 cost_price = 200.0, sales_price = 215.0,
                 entity_type = s1.category.entity_type,
                 entity_id = s1.id, organization=org)
    v2.save()
    v3 = Variant(title = "Kid's Haircut",
                 cost_price = 120.0, sales_price = 155.0,
                 entity_type = s1.category.entity_type,
                 entity_id = s1.id, organization=org)
    v3.save()
    v4 = Variant(title = "Women's Haircut",
                 cost_price = 310.0, sales_price = 375.0,
                 entity_type = s1.category.entity_type,
                 entity_id = s1.id, organization=org)
    v4.save()
    v5 = Variant(title = "Basic Manicure",
                 cost_price = 100.0, sales_price = 115.0,
                 entity_type = s2.category.entity_type,
                 entity_id = s2.id, organization=org)
    v5.save()
    v6 = Variant(title = "Basic Pedicure",
                 cost_price = 75.0, sales_price = 95.0,
                 entity_type = s2.category.entity_type,
                 entity_id = s2.id, organization=org)
    v6.save()
    v7 = Variant(title = "Massage 30 Mins",
                 cost_price = 200.0, sales_price = 245.0,
                 entity_type = s3.category.entity_type,
                 entity_id = s3.id, organization=org)
    v7.save()
    v8 = Variant(title = "Spa Treatment Ayurveda",
                 cost_price = 900.0, sales_price = 915.0,
                 entity_type = s4.category.entity_type,
                 entity_id = s4.id, organization=org)
    v8.save()
    v9 = Variant(title = "Spa Treatment Body Wrap",
                 cost_price = 700.0, sales_price = 755.0,
                 entity_type = s4.category.entity_type,
                 entity_id = s4.id, organization=org)
    v9.save()
    v10 = Variant(title = "Permanent Color",
                 cost_price = 100.0, sales_price = 115.0,
                 entity_type = s5.category.entity_type,
                 entity_id = s5.id, organization=org)
    v10.save()
    v11 = Variant(title = "Press & Curl",
                 cost_price = 200.0, sales_price = 215.0,
                 entity_type = s5.category.entity_type,
                 entity_id = s5.id, organization=org)
    v11.save()
    print("--- loadVariants ---")
    return {v1, v2, v3, v4, v5, v6, v7, v8, v9, v10, v11}


  def loadSessionStatus(self, org):
    SessionStatus.objects.all().delete()
    ss_1 = SessionStatus(title = "Open", organization=org)
    ss_1.save()
    ss_2 = SessionStatus(title = "Running", organization=org)
    ss_2.save()
    ss_3 = SessionStatus(title = "Closed", organization=org)
    ss_3.save()
    print("--- loadSessionStatus ---")
    return {ss_1, ss_2, ss_3}

  def loadSessions(self, ss_1, ss_2, ss_3, btc_will, btc_ben, btc_david, btc_james, btc_max, btc_noah, pos_m1, pos_m2, pos_m3, pos_m4, pos_w1, pos_w2, pos_w3, pos_k1, pos_k2, pos_k3, pos_k4, pos_k5, org):
    Session.objects.all().delete()
    s13 = Session(
      open_date_time = datetime.datetime(2024, 5, 1, 8, 00, 0 , 0, tzinfo=datetime.timezone.utc), close_date_time = datetime.datetime(2024, 5, 1, 8, 55, 0 , 0, tzinfo=datetime.timezone.utc),
                 pos = pos_k5, beautician = btc_will, status = ss_1, organization=org)
    s13.save()
    s12 = Session(
      open_date_time = datetime.datetime(2024, 12, 1, 8, 00, 0 , 0, tzinfo=datetime.timezone.utc), close_date_time = datetime.datetime(2024, 12, 1, 8, 55, 0 , 0, tzinfo=datetime.timezone.utc),
                 pos = pos_k4, beautician = btc_noah, status = ss_1, organization=org)
    s12.save()
    s11 = Session(
      open_date_time = datetime.datetime(2024, 12, 1, 8, 00, 0 , 0, tzinfo=datetime.timezone.utc), close_date_time = datetime.datetime(2024, 12, 1, 8, 55, 0 , 0, tzinfo=datetime.timezone.utc),
                 pos = pos_k3, beautician = btc_max, status = ss_1, organization=org)
    s11.save()
    s10 = Session(
      open_date_time = datetime.datetime(2024, 12, 1, 8, 00, 0 , 0, tzinfo=datetime.timezone.utc), close_date_time = datetime.datetime(2024, 12, 1, 8, 55, 0 , 0, tzinfo=datetime.timezone.utc),
                 pos = pos_k2, beautician = btc_james, status = ss_3, organization=org)
    s10.save()
    s9 = Session(
      open_date_time = datetime.datetime(2024, 12, 1, 8, 00, 0 , 0, tzinfo=datetime.timezone.utc), close_date_time = datetime.datetime(2024, 12, 1, 8, 55, 0 , 0, tzinfo=datetime.timezone.utc),
                 pos = pos_k1, beautician = btc_david, status = ss_3, organization=org)
    s9.save()
    s8 = Session(
      open_date_time = datetime.datetime(2024, 12, 1, 8, 00, 0 , 0, tzinfo=datetime.timezone.utc), close_date_time = datetime.datetime(2024, 12, 1, 8, 55, 0 , 0, tzinfo=datetime.timezone.utc),
                 pos = pos_w3, beautician = btc_ben, status = ss_2, organization=org)
    s8.save()
    s7 = Session(
      open_date_time = datetime.datetime(2024, 12, 1, 8, 00, 0 , 0, tzinfo=datetime.timezone.utc), close_date_time = datetime.datetime(2024, 12, 1, 8, 55, 0 , 0, tzinfo=datetime.timezone.utc),
                 pos = pos_w2, beautician = btc_will, status = ss_1, organization=org)
    s7.save()

    s6 = Session(
      open_date_time = datetime.datetime(2024, 10, 1, 8, 00, 0 , 0, tzinfo=datetime.timezone.utc), close_date_time = datetime.datetime(2024, 10, 1, 8, 55, 0 , 0, tzinfo=datetime.timezone.utc),
                 pos = pos_w1, beautician = btc_noah, status = ss_1, organization=org)
    s6.save()
    s5 = Session(
      open_date_time = datetime.datetime(2024, 10, 1, 8, 00, 0 , 0, tzinfo=datetime.timezone.utc), close_date_time = datetime.datetime(2024, 10, 1, 8, 55, 0 , 0, tzinfo=datetime.timezone.utc),
                 pos = pos_m4, beautician = btc_max, status = ss_1, organization=org)
    s5.save()
    s4 = Session(
      open_date_time = datetime.datetime(2024, 10, 1, 8, 00, 0 , 0, tzinfo=datetime.timezone.utc), close_date_time = datetime.datetime(2024, 10, 1, 8, 55, 0 , 0, tzinfo=datetime.timezone.utc),
                 pos = pos_m3, beautician = btc_james, status = ss_3, organization=org)
    s4.save()
    s3 = Session(
      open_date_time = datetime.datetime(2024, 10, 1, 8, 00, 0 , 0, tzinfo=datetime.timezone.utc), close_date_time = datetime.datetime(2024, 10, 1, 8, 55, 0 , 0, tzinfo=datetime.timezone.utc),
                 pos = pos_m3, beautician = btc_david, status = ss_3, organization=org)
    s3.save()
    s2 = Session(
      open_date_time = datetime.datetime(2024, 10, 1, 8, 00, 0 , 0, tzinfo=datetime.timezone.utc), close_date_time = datetime.datetime(2024, 10, 1, 8, 55, 0 , 0, tzinfo=datetime.timezone.utc),
                 pos = pos_m2, beautician = btc_ben, status = ss_2, organization=org)
    s2.save()
    s1 = Session(
      open_date_time = datetime.datetime(2024, 10, 1, 8, 00, 0 , 0, tzinfo=datetime.timezone.utc), close_date_time = datetime.datetime(2024, 10, 1, 8, 55, 0 , 0, tzinfo=datetime.timezone.utc),
                 pos = pos_m1, beautician = btc_will, status = ss_1, organization=org)
    s1.save()
    print("--- loadSessions ---")
    return {s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13}


  def loadOrders(self, sess1, sess2, sess3, sess4, sess5, sess6, sess7, sess8, sess9, sess10, sess11, sess12, sess13, cs_olivia, cs_emma, cs_thomas, cs_paul, cs_peter, org):
    Order.objects.all().delete()
    o13 = Order(
      order_code = "o-10012", receipt_number = "r-10012",
      customer = cs_thomas, session = sess13,
      total = 500.10, organization=org)
    o13.save()
    o12 = Order(
      order_code = "o-10011", receipt_number = "r-10011",
      customer = cs_emma, session = sess12,
      total = 455.50, organization=org)
    o12.save()
    o11 = Order(
      order_code = "o-10010", receipt_number = "r-10010",
      customer = cs_olivia, session = sess11,
      total = 155.45, organization=org)
    o11.save()

    o10 = Order(
      order_code = "o-10009", receipt_number = "r-10009",
      customer = cs_peter, session = sess10,
      total = 140.25, organization=org)
    o10.save()
    o9 = Order(
      order_code = "o-10008", receipt_number = "r-10008",
      customer = cs_paul, session = sess9,
      total = 390.8, organization=org)
    o9.save()
    o8 = Order(
      order_code = "o-10007", receipt_number = "r-10007",
      customer = cs_thomas, session = sess8,
      total = 800.0, organization=org)
    o8.save()
    o7 = Order(
      order_code = "o-10005", receipt_number = "r-10006",
      customer = cs_emma, session = sess7,
      total = 255.50, organization=org)
    o7.save()
    o6 = Order(
      order_code = "o-10005", receipt_number = "r-10005",
      customer = cs_olivia, session = sess6,
      total = 185.75, organization=org)
    o6.save()

    o5 = Order(
      order_code = "o-10004", receipt_number = "r-10005",
      customer = cs_peter, session = sess5,
      total = 450.0, organization=org)
    o5.save()
    o4 = Order(
      order_code = "o-10003", receipt_number = "r-10003",
      customer = cs_paul, session = sess4,
      total = 658.50, organization=org)
    o4.save()
    o3 = Order(
      order_code = "o-10002", receipt_number = "r-10002",
      customer = cs_thomas, session = sess3,
      total = 140.50, organization=org)
    o3.save()
    o2 = Order(
      order_code = "o-10001", receipt_number = "r-10001",
      customer = cs_emma, session = sess2,
      total = 875.0, organization=org)
    o2.save()
    o1 = Order(
      order_code = "o-10000", receipt_number = "r-10000",
      customer = cs_olivia, session = sess1,
      total = 900.50, organization=org)
    o1.save()
    print("--- loadOrders ---")
    return {o1, o2, o3, o4, o5, o6, o7, o8, o9, o10, o11, o12, o13}

  def loadOrderDetails(self, o1, o2, o3, o4, o5, o6, o7, o8, o9, o10, o11, o12, o13, et_service, s1, s2, s3, s4, s5, v1, v2, v3, v4, v5, v6, v7, v8, v9, v10, v11, org):
    od13 = OrderDetail(
      price = 353.23, quantity = 1,
      sub_total = 353.23, entity_id = s4.id,
      variant_id = v11.id,
      entity_type = et_service, order = o13, organization=org)
    od13.save()
    od12 = OrderDetail(
      price = 253.23, quantity = 1,
      sub_total = 253.23, entity_id = s3.id,
      variant_id = v10.id,
      entity_type = et_service, order = o12, organization=org)
    od12.save()
    od11 = OrderDetail(
      price = 213.23, quantity = 1,
      sub_total = 213.23, entity_id = s3.id,
      variant_id = v11.id,
      entity_type = et_service, order = o11, organization=org)
    od11.save()
    od10 = OrderDetail(
      price = 193.23, quantity = 1,
      sub_total = 193.23, entity_id = s2.id,
      variant_id = v10.id,
      entity_type = et_service, order = o10, organization=org)
    od10.save()
    od9 = OrderDetail(
      price = 191.23, quantity = 1,
      sub_total = 191.23, entity_id = s1.id,
      variant_id = v9.id,
      entity_type = et_service, order = o9, organization=org)
    od9.save()
    od8 = OrderDetail(
      price = 181.23, quantity = 1,
      sub_total = 181.23, entity_id = s2.id,
      variant_id = v8.id,
      entity_type = et_service, order = o8, organization=org)
    od8.save()
    od7 = OrderDetail(
      price = 171.23, quantity = 1,
      sub_total = 171.23, entity_id = s3.id,
      variant_id = v7.id,
      entity_type = et_service, order = o7, organization=org)
    od7.save()
    od6 = OrderDetail(
      price = 161.23, quantity = 1,
      sub_total = 161.23, entity_id = s4.id,
      variant_id = v6.id,
      entity_type = et_service, order = o6, organization=org)
    od6.save()
    od5 = OrderDetail(
      price = 151.23, quantity = 1,
      sub_total = 151.23, entity_id = s5.id,
      variant_id = v5.id,
      entity_type = et_service, order = o5, organization=org)
    od5.save()
    od4 = OrderDetail(
      price = 141.23, quantity = 1,
      sub_total = 141.23, entity_id = s4.id,
      variant_id = v4.id,
      entity_type = et_service, order = o4, organization=org)
    od4.save()
    od3 = OrderDetail(
      price = 131.23, quantity = 1,
      sub_total = 131.23, entity_id = s3.id,
      variant_id = v3.id,
      entity_type = et_service, order = o3, organization=org)
    od3.save()
    od2 = OrderDetail(
      price = 121.23, quantity = 1,
      sub_total = 121.23, entity_id = s2.id,
      variant_id = v2.id,
      entity_type = et_service, order = o2, organization=org)
    od2.save()
    od1 = OrderDetail(
      price = 111.23, quantity = 1,
      sub_total = 111.23, entity_id = s1.id,
      variant_id = v1.id,
      entity_type = et_service, order = o1, organization=org)
    od1.save()
    print("--- loadOrderDetails ---")
    return {od1, od2, od3, od4, od5, od6, od7, od8, od9, od10, od11, od12, od13}

  def resolve_salon_data_load(self, info, commandIn, **kwargs):

    org = Query.getOrganization(self)

    et_service, et_cp, et_sp, et_pos = Query.loadEntityTypes(self, org)
    ct_fs, ct_hb, ct_hc, ct_mk, ct_ms, ct_rt = Query.loadCategory(self, et_service, et_cp, org)

    Beautician.objects.all().delete()
    btc_will = Query.loadBeautician(self, "will_grant@tfax.com", "Will", "Grant", "1234567890", org)
    btc_ben = Query.loadBeautician(self, "ben_jesse@tfax.com", "Ben", "Jesse", "1234567890", org)
    btc_david = Query.loadBeautician(self, "david_griffin@tfax.com", "David", "Griffin", "1234567890", org)
    btc_james = Query.loadBeautician(self, "james_blake@tfax.com", "James", "Blake", "1234567890", org)
    btc_max = Query.loadBeautician(self, "max_gabriel@tfax.com", "Max", "Gabriel", "1234567890", org)
    btc_noah = Query.loadBeautician(self, "noah_franklin@tfax.com", "Noah", "Franklin", "1234567890", org)

    cs_olivia, cs_emma, cs_thomas, cs_paul, cs_peter = Query.loadSalonCustomers(self, et_service, et_cp, org)

    floor_men, floor_women, floor_kids = Query.loadFloorplan(self, org)

    pos_m1, pos_m2, pos_m3, pos_m4, pos_w1, pos_w2, pos_w3, pos_k1, pos_k2, pos_k3, pos_k4, pos_k5 = Query.loadPos(self, floor_men, floor_women, floor_kids, et_pos, org)

    mtype_1, mtype_2, mtype_3 = Query.loadMembershipType(self, org)

    p1, p2, p3, p4, p5, p6, p7 = Query.loadProducts(self, ct_rt, org)

    s1, s2, s3, s4, s5 = Query.loadServices(self, ct_fs, ct_hb, ct_hc, ct_mk, ct_ms, org)

    v1, v2, v3, v4, v5, v6, v7, v8, v9, v10, v11 = Query.loadVariants(self, s1, s2, s3, s4, s5, org)

    ss_1, ss_2, ss_3 = Query.loadSessionStatus(self, org)

    sess1, sess2, sess3, sess4, sess5, sess6, sess7, sess8, sess9, sess10, sess11, sess12, sess13 = Query.loadSessions(self, ss_1, ss_2, ss_3, btc_will, btc_ben, btc_david, btc_james, btc_max, btc_noah, pos_m1, pos_m2, pos_m3, pos_m4, pos_w1, pos_w2, pos_w3, pos_k1, pos_k2, pos_k3, pos_k4, pos_k5, org)

    OrderDetail.objects.all().delete()
    o1, o2, o3, o4, o5, o6, o7, o8, o9, o10, o11, o12, o13 = Query.loadOrders(self, sess1, sess2, sess3, sess4, sess5, sess6, sess7, sess8, sess9, sess10, sess11, sess12, sess13, cs_olivia, cs_emma, cs_thomas, cs_paul, cs_peter, org)
    Query.loadOrderDetails(self, o1, o2, o3, o4, o5, o6, o7, o8, o9, o10, o11, o12, o13, et_service, s1, s2, s3, s4, s5, v1, v2, v3, v4, v5, v6, v7, v8, v9, v10, v11, org)

    return DataLoadModelType(context = "salon-data-load",
                        status = f"Data Load Completed...")

schema_salon = graphene.Schema(query=Query)
