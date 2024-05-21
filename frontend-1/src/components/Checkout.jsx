import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import StripeCheckout from 'react-stripe-checkout';
import { placeOrder } from '../redux/order.slice';
import Error from './Error';
import Loader from './Loader';
import Success from './Success';

export default function Checkout({ amount }) {
  const dispatch = useDispatch();
  const orderState = useSelector((state) => state.orderReducer); 
  const cartreducerstate = useSelector((state) => state.cartReducer);
  const { cartItems } = cartreducerstate;
  const user = localStorage.getItem('currentUser')

  const data = JSON.parse(user);
  
  const currentUser = {
    id: data.id,
    name: data.name,
    email: data.email,
    is_staff: data.is_staff,
    is_active: data.is_active
  }


  const { placeOrderLoading, placeOrderSuccess, placeOrderError } = orderState;

  function tokenHandler(token) {
    dispatch(placeOrder({token: token, cartItems: cartItems, currentUser: currentUser,subtotal:amount}))
  }

  const validate = () => {
    if (!localStorage.getItem('currentUser')) {
      window.location.href = '/login';
    }
  };

  useEffect(() => {
    console.log(amount)
  }, [])

  return (
    <div>
      {placeOrderLoading && <Loader />}
      {placeOrderSuccess && (
        <Success success="Your Order Placed Successfully" />
      )}
      {placeOrderError && <Error error={placeOrderError} />}
      <StripeCheckout
        token={tokenHandler}
        amount={amount * 1000}
        shippingAddress
        currency="USD"
        stripeKey="pk_test_51PIlxZ02hF3Xt6GOvLtsFtczgYzdx5r8OBoVefaxg9HYB0NvGRNr0QO2lRFth8v9rnO3MqH2tLdlF0FaSOrX8Smb00rOEQ7GXh"
      >
        <button
          onClick={validate}
          class="text-white bg-gray-800 hover:bg-gray-900 focus:outline-none focus:ring-4 focus:ring-gray-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-gray-800 dark:hover:bg-gray-700 dark:focus:ring-gray-700 dark:border-gray-700"
        >
          PayNow
        </button>
      </StripeCheckout>
    </div>
  );
}
