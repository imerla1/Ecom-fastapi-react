import os
from uuid import uuid4

import stripe
from dto.orderschema import OrderCreatePlaceOrder
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from models.ordermodels import (OrderItemsModel, OrderModel,
                                ShippingAddressModel)
from sqlalchemy.orm import Session

stripe.api_key = "sk_test_51PIlxZ02hF3Xt6GOm2NT6nz6QXSV0q3NzMpE7t8sDqyu5cwLtM5Eg3UY2XsJ9JzZrQmPvZa6J1OwHNsnLHvctDna00wgEqbyqx"

class OrderService:
    def getAll(db: Session):
        orders_with_items = (
            db.query(OrderModel, OrderItemsModel)
            .join(OrderItemsModel, OrderModel.id == OrderItemsModel.order_id)
            .all()
        )
        result = []
        for order, order_item in orders_with_items:
            order_data = {
                "id": order.id,
                "name": order.name,
                "email": order.email,
                "orderAmount": order.orderAmount,
                "transactionId": order.transactionId,
                "isDelivered": order.isDelivered,
                "user_id": order.user_id,
                "created_at": order.created_at,
                "updated_at": order.updated_at,
                "order_items": {
                    "id": order_item.id,
                    "name": order_item.name,
                    "quantity": order_item.quantity,
                    "price": order_item.price,
                }
            }
            result.append(order_data)
    
        return jsonable_encoder(result)

    def createOrderPlace(request: OrderCreatePlaceOrder, db: Session):
        try:
            # Log the token to ensure it's being passed correctly
            print(f"Received token: {request.token.id}")
            print("ffwfwfw", request)

            customer = stripe.Customer.create(
                email=request.token.email, source=request.token.id
            )
            print(customer)

            payment = stripe.Charge.create(
                amount=request.subtotal * 100,  # Ensure amount is in cents
                currency="USD",
                customer=customer.id,
                receipt_email=request.token.email,
            )

            if payment:
                order_create = OrderModel(
                    user_id=request.currentUser.id,
                    name=request.currentUser.name,
                    email=request.currentUser.email,
                    orderAmount=request.subtotal,
                    transactionId=str(uuid4())
                )
                print(order_create, "ORD create")
                db.add(order_create)
                db.commit()

                db_orderid = db.query(OrderModel).filter(OrderModel.user_id == request.currentUser.id).first()

                shipping_a = ShippingAddressModel(
                    address=request.token.card.address_line1,
                    city=request.token.card.address_city,
                    country=request.token.card.address_country,
                    postalCode=request.token.card.address_zip,
                    order_id=db_orderid.id,
                )

                for dic in request.cartItems:
                    order_item_a = OrderItemsModel(
                        name=dic.name,
                        quantity=dic.quantity,
                        price=dic.price,
                        order_id=db_orderid.id,
                    )

                db.add(order_item_a)
                db.add(shipping_a)
                db.commit()
            else:
                print("Payment failed")
        except stripe.error.StripeError as e:
            # Handle specific Stripe errors
            print(f"Stripe error: {e.user_message}\nEXC{e}")
        except Exception as e:
            # Handle other possible errors
            print(f"An error occurred: {str(e)}")

        return request

    def getOrderById(id: int, db: Session):
        order_byid = db.query(OrderModel).filter(OrderModel.id == id).first()
        print("orderById-----------------", order_byid)

        orderItembyid = (
            db.query(OrderItemsModel).filter(OrderItemsModel.id == order_byid.id).all()
        )
        shippingByid = (
            db.query(ShippingAddressModel)
            .filter(ShippingAddressModel.id == order_byid.id)
            .first()
        )

        response = {
            "name": order_byid.name,
            "email": order_byid.email,
            "orderAmount": order_byid.orderAmount,
            "transactionId": order_byid.transactionId,
            "isDelivered": False,
            "user_id": order_byid.user_id,
            "created_at": order_byid.created_at,
            "updated_at": order_byid.updated_at,
            "orderItems": orderItembyid,
            "shippingAddress": shippingByid,
        }

        return response

    def getOrderByUserId(userid: int, db: Session):
        order_by_userid = (
            db.query(OrderModel).filter(OrderModel.user_id == userid).all()
        )

        return order_by_userid
