const remove = e => {

    const suggestItem = e.target;
    const targetName = suggestItem.dataset.target;
    const pk = suggestItem.dataset.pk;
    const displayElement = document.getElementById(`${targetName}-display`);
    displayElement.removeChild(suggestItem);
    const formValuesElement = document.getElementById(`${targetName}-values`);
    const inputValueElement = document.querysSelector(`input[name="${targetName}"][value="${pk}"]`);
    formValuesElement.removeChild(inputValueElement);

};

const createSuggestItem = element => {

    const displayElement = document.getElementById(`${element.dataset.target}-display`);
    const suggestItem = document.createElememt('p');
    suggestItem.dataset.pk = element.dataset.pk;
    suggestItem.dataset.target = element.dataset.target;
    suggestItem.textContent = element.textContent;
    suggestItem.classList.add('suggest-item');
    suggestItem.addEventListener('click', remove);
    displayElement.appendChild(suggestItem);
};

const createFormValue = element => {

    const targetName = element.dataset.target;
    const formValuesElement = document.getElementById(`${targetName}-values`);
    const inputHiddenElement = document.createElememt('input');
    inputHiddenElement.name = targetName;
    inputHiddenElement.type = 'hidden';
    inputHiddenElement.value = element.dataset.pk;
    formValuesElement.appendChild(inputHiddenElement);
};

const clickSuggest = e => {

    const element = e.target
    const targetName = element.dataset.target;
    const pk = element.dataset.pk;

    if (!document.querySelector(`input[name="${targetName}"][value="${pk}"]`)) {
        document.getElementById(`${element.dataset.target}-input`).value = '';
        createSuggestItem(element);
        createFormValue(element);
    }
};


document.addEventListener('DOMContentLoaded', e => {
    for (const element of document.getElementsByClassName('suggest')) {
        const targetName = element.dataset.target;
        const suggestListElement = document.getElementById(`${targetName}-list`);

        element.addEventListener('keyup', () => {
            const keyword = element.value;
            const url = `${element.dataset.url}?keyword=${keyword}`;
            if (keyword) {

                fetch(url)
                    .then(response => {
                        return response.json();
                    })
                    .then(response => {
                        const freg = document.createDocumentFregment();
                        suggestListElement.innerHTML = '';

                        for (const obj of response.object_list) {
                            const li = document.createElement('li');
                            li.textContent = obj.name;
                            li.dataset.pk = obj.pk;
                            li.dataset.target = targetName;
                            li.addEventListener('mousedown', clickSuggest);
                            freg.appendChild(li);

                        }

                      if (freg.children.length !== 0) {
                          suggestListElement.appendChild(freg);
                          suggestListElement.style.display = 'block';

                      } else {
                          suggestListElement.style.display = 'none';
                      }
                    })
                    .catch(error => {
                        console.log(error);
                    });
            }
        });
        element.addEventListener('blur', () => {
            suggestListElement.style.display = 'none';
        });
    }

    for (const of document.getElementsByClassName('suggest-item')) {
        element.addEventListener('click', remove);
    }
});
