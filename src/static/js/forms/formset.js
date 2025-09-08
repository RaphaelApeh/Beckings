// Product Formset

const emptyForm = document.querySelector("#emptyForm");
const totalForm = document.querySelector("#totalForm");
const totalFormset = document.querySelector("#id_form-TOTAL_FORMS");
const maxFormset = document.querySelector("#id_form-MAX_NUM_FORMS");
const addBtn = document.querySelector("#addBtn");


function handleFormSet(event){
    if (!event){
        let msg = ""
        throw new Error(msg)
    }
    event.preventDefault();

    const cloneForm = emptyForm.cloneNode(true);
    cloneForm.setAttribute("class", "");
    const totalForms = document.querySelectorAll("#forms");
    const TotalFormCount = totalForms.length;
    const regex = new RegExp("__prefix__", "g");
    cloneForm.innerHTML = cloneForm.innerHTML.replace(regex, TotalFormCount);
    cloneForm.setAttribute("id", "forms");
    totalFormset.value = parseInt(TotalFormCount + 1);
    if (parseInt(totalFormset.value) >= parseInt(maxFormset.value)){
        let msg = "Can't add more forms :(";
        const errorMsg = document.querySelector("#errorMsg");
        errorMsg.classList.remove("hidden");
        const innerDiv = document.createElement("div");
        innerDiv.setAttribute("class", "text-sm opacity-80");
        innerDiv.innerText = msg
        errorMsg.appendChild(innerDiv)
        return
    }
    totalForm.append(cloneForm);
    
}

addBtn.addEventListener("click", handleFormSet);
