def access_control(
    is_admin: bool,
    is_owner: bool,
    is_public: bool,
    is_logged_in: bool,
) -> bool:
    """
    Concede acesso quando:
      - (admin OU dono do recurso)  E  (recurso público OU usuário logado)

    Expressão MC/DC: (A or B) and (C or D)
      A = is_admin
      B = is_owner
      C = is_public
      D = is_logged_in
    """
    return (is_admin or is_owner) and (is_public or is_logged_in)
