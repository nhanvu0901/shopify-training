
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




                                 let list_origin = JSON.parse(cart_data.responseText).items
                                 let list_new = combo.products
                                 let list_product_not_sale = []

                                const arrayIds = list_new.map(item => item.product_id);

                                list_origin.forEach(item => {
                                  if (!arrayIds.includes(item.product_id.toString())) {
                                    list_product_not_sale.push(item);
                                  }
                                });

                                console.log(list_product_not_sale);






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
                                  list_product_not_sale.forEach(item=>{
                                      let final_price = item.price.toString().substring(0, item.price.toString().length - 2)
                                    discount_money +=Number(final_price)
                                })
                                 console.log(discount_money)
                                 let final_price = document.getElementsByClassName("cart__footer")
                                 let discount_price_node = document.createElement("DIV")
                                 discount_price_node.classList.add("discount-container")
                                 let note_span = document.createElement("SPAN")
                                 let money_span = document.createElement("SPAN")
                                if(combo.has_many_combo) {
                                    note_span.innerHTML = "Your cart contain "+combo.has_many_combo+" combo discount with " + combo.discount_amount + " off each combo" + "<br>"
                                }
                                else{
                                    note_span.innerHTML = "Your cart contain discount combo with " + combo.discount_amount + " off" + "<br>"
                                }




                                 discount_price_node.appendChild(note_span)
                                 money_span.classList.add("discount-money")
                                if(combo.has_many_combo){
                                    money_span.innerHTML ="Final price: "+discount_money *parseInt(combo.has_many_combo) +" "+currency
                                }
                                else{
                                 money_span.innerHTML ="Final price: "+discount_money +" "+currency
                                }
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
                                let new_list_product_not_sale =list_product_not_sale.map(obj => ({ ...obj, ["is_bundle_product_sale"]: false }));

                                let new_data = JSON.parse(JSON.parse(data.responseText).result).products.map(obj => ({ ...obj, ["is_bundle_product_sale"]: true }));
                                param={
                                    origin_data : cart_data.responseText,
                                    send:new_data,
                                    discount_amount:JSON.parse(JSON.parse(data.responseText).result).discount_amount,
                                    list_product_not_sale:new_list_product_not_sale,
                                    discount:discount_money,
                                    shop_url:window.shopUrl
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