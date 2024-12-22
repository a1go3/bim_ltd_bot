from flask import flash, redirect, render_template, request, url_for

from db.models import Brand, UserRoleType

from . import app
from .crud import crud_brand
from .permission import requires_permission


@app.route("/admin/brands", methods=["GET", "POST"])
@requires_permission("view")
async def brand_list_view(user):
    """Отображение списка брендов."""
    if request.method == "POST":
        if user.role != UserRoleType.SUPERUSER:
            flash("У вас недостаточно прав для удаления.", "danger")
            return redirect(request.referrer or url_for("brand_list_view"))
        brand_id = int(request.form["object_id"])
        await crud_brand.delete_object(brand_id)
    brand_list = await crud_brand.get_object_list()
    context = {"table": Brand, "object_list": brand_list}
    return render_template("object.html", **context)


@app.route("/admin/brands/add", methods=["GET", "POST"])
@requires_permission("create")
async def brand_add_view():
    """Добавление нового бренда."""
    if request.method == "POST":
        form_data = request.form.to_dict()
        await crud_brand.add_object(form_data)
        return redirect(url_for("brand_list_view"))
    return render_template("form_add.html")


@app.route("/admin/brands/<int:id>", methods=["GET", "POST"])
@requires_permission("edit")
async def brand_edit_view(id):
    """Редактирование бренда."""
    if request.method == "POST":
        form_data = request.form.to_dict()
        await crud_brand.edit_object(form_data, id)
        return redirect(url_for("brand_list_view"))
    return render_template("form_edit.html")
