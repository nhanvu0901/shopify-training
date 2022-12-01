
function initJQuery(e) {
    var t;
    "undefined" == typeof jQuery ? ((t = document.createElement("SCRIPT")).src = "https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js", t.type = "text/javascript", t.onload = e, document.head.appendChild(t)) : e()
}

initJQuery(function () {
    if (window.location.href.slice(-4) === "cart") {
           jQuery.ajax({
                        type: "GET",
                        url: window.shopUrl+"/cart.json",
                        contentType: "application/json",
                        async:true,
                        crossDomain:true,
                        processData: false,
                        error: function (request, error) {
                            console.log(error)
                        },
                        complete(cart_data) {
                          let response =JSON.parse(cart_data.responseText).items
                          console.log(response)

                            jQuery.ajax({
                        type: "POST",
                        url: "https://odoo.website/shopify/cart",
                        data: cart_data.responseText,
                        contentType: "application/json",
                        async:true,
                        crossDomain:true,
                        processData: false,
                        error: function (request, error) {
                            console.log(error)
                        },
                        complete(data) {
                            if(JSON.parse(JSON.parse(data.responseText).result)){
                                 let combo = JSON.parse(JSON.parse(data.responseText).result)
                                console.log(combo)
                                 let currency = combo.currency
                                 let discount = combo.discount_amount
                                 let sum_money = 0;
                                 let discount_money = 0;
                                combo.products.forEach(product=>{
                                  let per_item = product.product_price *product.quantity
                                  sum_money +=per_item
                                })
                                if(discount.charAt(discount.length-1)==='%'){
                                    let percent =parseInt(combo.discount_amount.substring(0,combo.discount_amount.length))
                                    discount_money = sum_money-sum_money*(percent/100)
                                }
                                 else{
                                     let amount =parseInt(combo.discount_amount)
                                     discount_money = sum_money-amount
                                }
                                 console.log(discount_money)
                                 let final_price = document.getElementsByClassName("cart__footer")
                                 let discount_price_node = document.createElement("DIV")
                                 discount_price_node.classList.add("discount-container")
                                 let note_span = document.createElement("SPAN")
                                 let money_span = document.createElement("SPAN")
                                 note_span.innerHTML = "Your cart contain discount combo with "+combo.discount_amount +" off" +"<br>"
                                 discount_price_node.appendChild(note_span)
                                 money_span.classList.add("discount-money")
                                 money_span.innerHTML ="Final price: "+discount_money +" "+currency
                                 discount_price_node.appendChild(money_span)
                                 final_price[0].appendChild(discount_price_node)
                                 document.head.innerHTML += `
                                              <style>
                                                .discount-container .discount-money{
                                                 color: red;
                                                 font-size: 2rem;
                                                }
                                              </style>`


                                var btn = document.getElementById('checkout');

                                btn.removeAttribute('type');
                                btn.removeAttribute('form');
                                btn.setAttribute('onclick','CheckOut();');
                                btn.onclick = function() {CheckOut();};

                                param={
                                    send:data,
                                    discount:discount_money
                                }
                                function CheckOut() {

                                    var xmlhttp = new XMLHttpRequest();

                                    xmlhttp.open("POST", "https://odoo.website/shopify/checkout");
                                    xmlhttp.setRequestHeader("Content-Type", "application/json");
                                    xmlhttp.onreadystatechange = function () {
                                            if (xmlhttp.readyState == 4) {
                                                if (xmlhttp.status == 200) {
                                                    console.log(xmlhttp.responseText);
                                                    window.location.href = JSON.parse(JSON.parse(xmlhttp.responseText).result);
                                                }
                                            }
                                        };
                                    xmlhttp.send(JSON.stringify(param))


                              // jQuery.ajax({
                              //   type: "POST",
                              //   url: "https://odoo.website/shopify/checkout",
                              //   data: JSON.stringify(param),
                              //   contentType: "application/json",
                              //   async:true,
                              //   crossDomain:true,
                              //   processData: false,
                              //
                              //   error: function (request, error) {
                              //       console.log(error)
                              //   },
                              //   complete(data){
                              //       console.log(data)
                              //   }}




                            }



                        }}
                 })
                        }
           })
        }


})