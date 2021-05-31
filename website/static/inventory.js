function deleteItem(item_id) {
    fetch('delete_item', {
        method: 'POST',
        body: JSON.stringify({item_id: item_id})
    }). then((_res) => {
        window.location.href = "/";
    })
}