## B3
### Two Issues
1. `self.save()` inside `validate()` can call `validate()` again and cause a loop.
2. `unit.save()` should not be done inside `validate()`. Move it to `on_submit()`.
## Correct Code
```python
def validate(self):
    self.rental_total = sum(r.line_amount for r in self.items)
def on_submit(self):
    unit = frappe.get_doc(
        "Equipment Unit",
        self.items[0].equipment_unit
    )
    unit.current_status = "Rented"
    unit.save()

```
## B4
If two staff members open the same booking at the same time, the first person who saves it changes the document.
When the second person tries to save the old version, Frappe shows:
**"Document has been modified after you have opened it."**
Frappe uses optimistic locking to prevent the second user from overwriting the first user's changes.

## on_update() — Recursion Problem
`on_update()` runs when a document is updated.
If we use `self.save()` inside `on_update()`, it saves the document again.
This runs `on_update()` again and creates a loop
So, we should not use `self.save()` inside `on_update()`
Instead, calculate `final_amount` inside `validate()` before saving

## H1
## Why `frappe.call()` should not be used inside `validate`
`frappe.call()` takes time to get a response.
But `validate` needs to finish the check immediately.
So the server response may come after validation is already finished.
Therefore, use `onload` or `refresh` for availability checks.
The server should still check availability before saving or submitting.

## I1 -SQL parameterized
The f-string method puts values directly into the sql query.
The parameterized method keeps the values separate from the query and the parameterized method is safer and helps prevent sql injection
So, we should use the parameterized method.

### ignore_permissions=True
- `doc.insert(ignore_permissions=True)`  
  Used to create default Equipment Categories during installation.
- `settings.save(ignore_permissions=True)`  
  Used to save the default RentFlow Settings during installation.
- `invoice.insert(ignore_permissions=True)`  
  Used to automatically create the Rental Invoice after submission.
- `invoice.delete(ignore_permissions=True)`  
  Used to delete an unpaid draft invoice when the booking is cancelled.
- Equipment status update  
  Used to change the equipment status to `Reserved` during booking submission.


## J1-Jinja
`frappe.get_all()` can get data directly inside the Jinja template.
`before_print()` can get the data earlier and store it in `doc.precomputed_field`.
Using `before_print()` keeps the Jinja template simple because it only displays the prepared data.