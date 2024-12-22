from flask import flash, redirect, render_template, request, url_for

from db.models import TypeProduct, UserRoleType

from . import app
from .crud import crud_typeproduct
from .permission import requires_permission


@app.route("/admin/typeproducts", methods=["GET", "POST"])
@requires_permission("view")
async def typeproduct_list_view(user):
    """Отображение списка типов продукта."""
    if request.method == "POST":
        if user.role != UserRoleType.SUPERUSER:
            flash("У вас недостаточно прав для удаления.", "danger")
            return redirect(
                request.referrer or url_for("typeproduct_list_view")
            )
        typeproduct_id = int(request.form["object_id"])
        await crud_typeproduct.delete_object(typeproduct_id)
    typeproduct_list = await crud_typeproduct.get_object_list()
    context = {
        "table": TypeProduct,
        "object_list": typeproduct_list,
    }
    return render_template("object.html", **context)


@app.route("/admin/typeproducts/add", methods=["GET", "POST"])
@requires_permission("create")
async def typeproduct_add_view(user):
    """Добавление нового типа продукта."""
    if request.method == "POST":
        form_data = request.form.to_dict()
        await crud_typeproduct.add_object(form_data)
        return redirect(url_for("typeproduct_list_view"))
    return render_template("form_add.html")


@app.route("/admin/typeproducts/<int:id>", methods=["GET", "POST"])
@requires_permission("edit")
async def typeproduct_edit_view(user, id):
    """Редактирование типа продукта."""
    if request.method == "POST":
        form_data = request.form.to_dict()
        await crud_typeproduct.edit_object(form_data, id)
        return redirect(url_for("typeproduct_list_view"))
    return render_template("form_edit.html")
