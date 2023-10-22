$(document).ready(function () {

    $('.payWithRazorpay').click(function (e) {
        e.preventDefault();


        var address_id = $("[name='selected_address']").val();
        var grand_amount = $("[name='grand_amount']").val(); // final_amount to be paid
        var amount_to_be_paid = $("[name='amount_to_be_paid']").val(); // amount to be paid 
        var used_wallet_amount = $("[name='used_wallet_amount']").val(); // used wallet amount  
        console.log(address_id);
        console.log(amount_to_be_paid);
        console.log(grand_amount);
        console.log("Wallet Amount", used_wallet_amount);
        var token = $("[name='csrfmiddlewaretoken']").val();
        console.log("part - 1");


        if (address_id == "") {
            alert("Field is mandatory");
            return false;
        }
        else {
            console.log("part-2");
            data = {
                "grand_amount": grand_amount,
            }
            $.ajax({
                url: "proceed-to-pay/",
                method: "GET",
                data: data,
                success: function (response) {
                    // console.log("Address :-", address_id);
                    // console.log("proceed to pay...success ")
                    var amount = response.final_amount
                    console.log(response.grand_amount);
                    console.log(response.final_amount);
                    console.log("part-3");

                    var options = {
                        "key": "rzp_test_FZKNhgobDlZM2U", // Enter the Key ID generated from the Dashboard
                        //"amount": amount, `Amount is in currency subunits. Default currency is INR. Hence, 50000 refers to 50000 paise
                        "amount": amount * 100,
                        "currency": "INR",
                        "name": "Time Horizon",
                        "description": "Thank you for buying from us",
                        "image": "https://example.com/your_logo",
                        // "order_id": "order_IluGWxBm9U8zJ8", //This is a sample Order ID. Pass the `id` obtained in the response of Step 1
                        "handler": function (response_a) {
                            data = {
                                'used_wallet_amount': used_wallet_amount,
                                'grand_amount': grand_amount,
                                'selected_address': address_id,
                                'paymentMethod': "Paid by razorpay",
                                'payment_id': response_a.razorpay_payment_id,
                                csrfmiddlewaretoken: token,
                            }

                            $.ajax({
                                type: "POST",
                                url: "confirm-order/",
                                data: data,
                                success: function (res) {
                                    var order_number=res.order_number
                                    swal('Congrats', res.status, 'success').then((value) => {
                                        window.location.href = 'success/' + order_number + '/';
                                    });

                                },
                                error: (xhr, textStatus, errorThrown) => {
                                    console.log("AJAX request failed. Status: " + textStatus + ", Error: " + errorThrown);

                                }
                            });

                        },
                        "prefill": {
                            "name": "Gaurav Kumar",
                            "email": "gaurav.kumar@example.com",
                            "contact": "9000090000"
                        },
                        "notes": {
                            "address": "Razorpay Corporate Office"
                        },
                        "theme": {
                            "color": "#3399cc"
                        }
                    };
                    var rzp1 = new Razorpay(options);

                    rzp1.open();
                }
            })


        }

    });
});


// rzp_test_FZKNhgobDlZM2U -- key id
// v8x6aZomko3m3MQ9spoOuLBw  -- secret key