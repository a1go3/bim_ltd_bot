from flask import flash, redirect, render_template, request, url_for

from db.models import Product, ProductCharacterAssociation, UserRoleType

from . import app
from .crud import crud_brand, crud_character, crud_product, crud_typeproduct
from .permission import requires_permission


@app.route("/admin/products", methods=["GET", "POST"])
@requires_permission("view")
async def product_list_view(user):
    """Отображение списка продуктов."""
    if request.method == "POST":
        if user.role != UserRoleType.SUPERUSER:
            flash("У вас недостаточно прав для удаления.", "danger")
            return redirect(request.referrer or url_for("brand_list_view"))
        product_id = int(request.form["object_id"])
        await crud_product.delete_object(product_id)
    # filter
    # if request.args:
    #    field = request.args['filter']
    #    value = int(request.args['value'])
    #    field = Product.__table__.columns[field]
    #    print(f'Field: {field}, Type: {type(field)}')
    product_list = await crud_product.get_object_list()
    brand_list = [
        (brand.id, brand.name) for brand in await crud_brand.get_object_list()
    ]
    character_list = [
        (character.id, character.name)
        for character in await crud_character.get_object_list()
    ]
    type_product_list = [
        (type_product.id, type_product.name)
        for type_product in await crud_typeproduct.get_object_list()
    ]
    context = {
        "table": Product,
        "object_list": product_list,
        "brand_list": brand_list,
        "character_list": character_list,
        "type_product_list": type_product_list,
    }
    return render_template("object.html", **context)


@app.route("/admin/products/add", methods=["GET", "POST"])
@requires_permission("create")
async def product_add_view():
    """Добавление нового продукта."""
    if request.method == "POST":
        form_data = request.form.to_dict()
        characters_data = request.form.getlist("character_id")
        await crud_product.add_object(
            form_data, ProductCharacterAssociation, characters_data
        )
        return redirect(url_for("product_list_view"))
    return render_template("form_add.html")


@app.route("/admin/products/<int:id>", methods=["GET", "POST"])
@requires_permission("edit")
async def product_edit_view(id):
    """Редактирование продукта."""
    if request.method == "POST":
        form_data = request.form.to_dict()
        characters_data = request.form.getlist("character_id")
        await crud_product.edit_object(
            form_data, id, ProductCharacterAssociation, characters_data
        )
        return redirect(url_for("product_list_view"))
    return render_template("form_edit.html")
