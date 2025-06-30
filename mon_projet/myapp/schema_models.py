import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Tables et leurs attributs
tables = {
    "User": [
        "id (PK)",
        "name",
        "email",
        "password",
        "role [gestion|commercial|support]"
    ],
    "Client": [
        "id (PK)",
        "full_name",
        "email",
        "phone",
        "company_name",
        "created_date",
        "last_contact_date",
        "commercial_id (FK → User.id)"
    ],
    "Contract": [
        "id (PK)",
        "client_id (FK → Client.id)",
        "commercial_id (FK → User.id)",
        "total_amount",
        "amount_due",
        "created_date",
        "is_signed [0|1]"
    ],
    "Event": [
        "id (PK)",
        "contract_id (FK → Contract.id)",
        "support_id (FK → User.id)",
        "start_date",
        "end_date",
        "location",
        "attendees",
        "notes"
    ],
}

# Position manuelle des tables (x, y)
# Y diminue vers le bas (matplotlib)
positions = {
    "User": (0, 0),
    "Client": (4, 0),
    "Contract": (4, -4),
    "Event": (8, -4),
}

fig, ax = plt.subplots(figsize=(12, 6))
ax.set_xlim(-1, 10)
ax.set_ylim(-6, 1)
ax.axis('off')

def draw_table(ax, x, y, name, attrs):
    # Dimensions
    width = 3
    header_height = 0.5
    attr_height = 0.3
    height = header_height + len(attrs)*attr_height

    # Contour complet
    rect = patches.Rectangle((x, y - height), width, height,
                             linewidth=1.2, edgecolor='black', facecolor='white')
    ax.add_patch(rect)

    # Bandeau du nom
    header_rect = patches.Rectangle((x, y - header_height), width, header_height,
                                    linewidth=1.2, edgecolor='black', facecolor='lightblue')
    ax.add_patch(header_rect)

    # Nom table centré en gras
    ax.text(x + width/2, y - header_height/2, name,
            ha='center', va='center', fontsize=12, fontweight='bold')

    # Liste des attributs, alignés à gauche
    for i, attr in enumerate(attrs):
        ax.text(x + 0.1, y - header_height - (i + 0.7)*attr_height, attr,
                ha='left', va='center', fontsize=10, family='monospace')

# Dessin des tables
for table_name, attrs in tables.items():
    x, y = positions[table_name]
    draw_table(ax, x, y, table_name, attrs)

# Fonction pour dessiner des flèches en "L"
def draw_L_arrow(ax, start, mid, end):
    # Ligne verticale ou horizontale
    ax.annotate("",
                xy=mid, xytext=start,
                arrowprops=dict(arrowstyle='-', color='gray', lw=1.5))
    # Ligne avec flèche
    ax.annotate("",
                xy=end, xytext=mid,
                arrowprops=dict(arrowstyle='->', color='gray', lw=1.5))

# Relations à dessiner (de → vers)
# On utilise les coordonnées des centres des côtés droits/gauches des rectangles
# Chaque rectangle a width=3, hauteur variable, mais on prend un repère simple
# Pour garder simple, on place les flèches entre centres verticaux des tables

# Points pour flèches:
# User box (0,0), height = 0.5 + 5*0.3 = 2, center y = 0 - 2/2 = -1
user_center = (0 + 3, 0 - 2/2)

# Client box (4,0), height= 0.5 + 8*0.3 = 2.9, center y = 0 - 2.9/2 = -1.45
client_center = (4, 0 - 2.9/2)

# Contract box (4,-4), height=0.5+7*0.3=2.6, center y = -4 - 2.6/2 = -5.3
contract_center = (4, -4 - 2.6/2)

# Event box (8,-4), height=0.5+8*0.3=2.9, center y = -4 - 2.9/2 = -5.45
event_center = (8, -4 - 2.9/2)

# Dessiner flèches
# Client → User (de gauche Client vers droite User)
start = (4, client_center[1])
mid = (1.5, client_center[1])
end = (1.5, user_center[1])
draw_L_arrow(ax, start, mid, end)

# Contract → Client
start = (4, contract_center[1])
mid = (6.5, contract_center[1])
end = (6.5, client_center[1])
draw_L_arrow(ax, start, mid, end)

# Contract → User
start = (4, contract_center[1])
mid = (6.5, contract_center[1])
end = (6.5, user_center[1])
draw_L_arrow(ax, start, mid, end)

# Event → Contract
start = (8, event_center[1])
mid = (6.5, event_center[1])
end = (6.5, contract_center[1])
draw_L_arrow(ax, start, mid, end)

# Event → User
start = (8, event_center[1])
mid = (9.5, event_center[1])
end = (9.5, user_center[1])
draw_L_arrow(ax, start, mid, end)

plt.title("Diagramme UML simplifié", fontsize=16, fontweight='bold')
plt.tight_layout()
plt.show()
