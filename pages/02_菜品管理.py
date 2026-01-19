import streamlit as st
from pathlib import Path
import uuid

from services.repo_products import list_all_products, add_product, delete_product, update_product
from services.layout_merchant import (
    init_session, hide_pages, require_merchant, render_sidebar
)

init_session()
hide_pages()
require_merchant()
render_sidebar()




if st.session_state.user["role"] != "merchant":
    st.error("仅商家可访问")
    st.stop()

st.title("🧾 菜品管理（本地图片）")

IMG_DIR = Path(__file__).resolve().parent.parent / "assets" / "product_images"
IMG_DIR.mkdir(parents=True, exist_ok=True)

def save_image(uploaded_file) -> str:
    ext = Path(uploaded_file.name).suffix.lower()
    if ext not in [".png", ".jpg", ".jpeg", ".webp"]:
        raise ValueError("仅支持 png/jpg/jpeg/webp")
    fname = f"{uuid.uuid4().hex}{ext}"
    fpath = IMG_DIR / fname
    fpath.write_bytes(uploaded_file.getbuffer())
    return str(Path("assets") / "product_images" / fname)

# ===== 新增菜品 =====
with st.expander("➕ 新增菜品", expanded=False):
    name = st.text_input("菜名", key="add_name")
    category = st.text_input("分类", key="add_category")
    price = st.number_input(
        "价格", min_value=0.0, value=10.0, step=1.0, key="add_price"
    )

    description = st.text_area("描述（可选）", key="add_description")
    image = st.file_uploader(
        "上传菜品图片（本地）",
        type=["png", "jpg", "jpeg", "webp"],
        key="add_image"
    )


    if st.button("新增", use_container_width=True):
        try:
            img_path = save_image(image) if image else None

            add_product(
                name=name.strip(),
                category=category.strip(),
                price=price,
                description=description.strip(),
                is_active=1,
                image_path=img_path
            )


            # ===== ⭐ 清空新增表单 =====
            for k in [
                "add_name",
                "add_category",
                "add_price",
                "add_tags",
                "add_description",
                "add_image",
            ]:
                if k in st.session_state:
                    del st.session_state[k]

            st.success("已新增，可继续添加下一道菜")
            st.rerun()

        except Exception as e:
            st.error(f"新增失败：{e}")


st.divider()
rows = list_all_products()
rows = sorted(rows, key=lambda x: x["id"])

if not rows:
    st.info("暂无菜品")
    st.stop()

# ===== 已有菜品 =====
for idx, p in enumerate(rows, start=1):
    with st.container(border=True):
        c1, c2 = st.columns([2, 3])

        with c1:
            st.write(f"**{idx}. {p['name']}**")
            if p["image_path"]:
                st.image(p["image_path"], use_container_width=True)
            else:
                st.caption("暂无图片")

        with c2:
            st.caption(f"分类：{p['category'] or '-'}")
            st.write(f"价格：¥{float(p['price']):.2f}")
            if p["description"]:
                st.write(p["description"])

            with st.expander("✏️ 编辑（可重新上传图片）", expanded=False):
                ename = st.text_input("菜名", value=p["name"], key=f"n{p['id']}")
                ecat = st.text_input("分类", value=p["category"] or "", key=f"c{p['id']}")
                eprice = st.number_input("价格", min_value=0.0, value=float(p["price"]), step=1.0, key=f"p{p['id']}")
                edesc = st.text_area("描述", value=p["description"] or "", key=f"d{p['id']}")

                eupload = st.file_uploader(
                    "重新上传图片（可选）",
                    type=["png", "jpg", "jpeg", "webp"],
                    key=f"img{p['id']}"
                )

                if st.button("保存修改", key=f"save{p['id']}", use_container_width=True):
                    try:
                        img_path = p["image_path"]
                        if eupload:
                            img_path = save_image(eupload)

                        update_product(
                            pid=p["id"],
                            name=ename.strip(),
                            category=ecat.strip(),
                            price=eprice,
                            is_active=1,
                            description=edesc.strip(),
                            image_path=img_path
                        )

                        st.success("已保存")
                        st.rerun()
                    except Exception as e:
                        st.error(f"保存失败：{e}")

            if st.button("删除", key=f"del{p['id']}", use_container_width=True):
                delete_product(p["id"])
                st.rerun()
