from flask import flash, redirect, render_template, request, url_for

from db.models import Character, UserRoleType

from . import app
from .crud import crud_character
from .permission import requires_permission


@app.route("/admin/characters", methods=["GET", "POST"])
@requires_permission("view")
async def character_list_view(user):
    """Отображение списка характеристик."""
    if request.method == "POST":
        if user.role != UserRoleType.SUPERUSER:
            flash("У вас недостаточно прав для удаления.", "danger")
            return redirect(request.referrer or url_for("character_list_view"))
        character_id = int(request.form["object_id"])
        await crud_character.delete_object(character_id)
    character_list = await crud_character.get_object_list()
    context = {
        "table": Character,
        "object_list": character_list,
    }
    return render_template("object.html", **context)


@app.route("/admin/characters/add", methods=["GET", "POST"])
@requires_permission("create")
async def character_add_view():
    """Добавление новой характеристики."""
    if request.method == "POST":
        form_data = request.form.to_dict()
        await crud_character.add_object(form_data)
        return redirect(url_for("character_list_view"))
    return render_template("form_add.html")


@app.route("/admin/characters/<int:id>", methods=["GET", "POST"])
@requires_permission("edit")
async def character_edit_view(id):
    """Редактирование характеристики."""
    if request.method == "POST":
        form_data = request.form.to_dict()
        await crud_character.edit_object(form_data, id)
        return redirect(url_for("character_list_view"))
    return render_template("form_edit.html")
