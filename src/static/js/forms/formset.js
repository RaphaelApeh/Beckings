// Product Formset

const emptyForm = document.querySelector("#emptyForm");
const totalForm = document.querySelector("#totalForm");
const totalFormset = document.querySelector("#id_form-TOTAL_FORMS");
const addBtn = document.querySelector("#addBtn");

console.log("Empty Form", emptyForm)
console.log("TOtal Form", totalForm)

function handleFormSet(event=null){
    if (!event){
        const msg = ""
        throw new Error(msg)
    }
    event.preventDefault();

    const cloneForm = emptyForm.cloneNode(true);
    cloneForm.setAttribute("class", "");
    cloneForm.setAttribute("id", "");
    const totalForms = document.querySelectorAll("#forms");
    const TotalFormCount = totalForms.length;
    const regex = new RegExp("__prefix__", "g");
    cloneForm.innerHTML = cloneForm.innerHTML.replace(regex, TotalFormCount);
    cloneForm.setAttribute("id", "forms")
    totalFormset.value = parseInt(TotalFormCount + 1);
    totalForm.append(cloneForm);
    
}

addBtn.addEventListener("click", handleFormSet);
