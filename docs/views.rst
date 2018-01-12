*****
Views
*****

Hunt Views
==========

.. autofunction:: huntserver.hunt_views.protected_static(request, file_path)
.. autofunction:: huntserver.hunt_views.hunt(request, hunt_num)
.. autofunction:: huntserver.hunt_views.current_hunt(request)
.. autofunction:: huntserver.hunt_views.puzzle_view(request, puzzle_id)
.. autofunction:: huntserver.hunt_views.chat(request)
.. autofunction:: huntserver.hunt_views.unlockables(request)

Info Views
==========

.. autofunction:: huntserver.info_views.index(request)
.. autofunction:: huntserver.info_views.current_hunt_info(request)
.. autofunction:: huntserver.info_views.previous_hunts(request)
.. autofunction:: huntserver.info_views.registration(request)

Staff Views
===========

.. autofunction:: huntserver.staff_views.queue(request, page_num)
.. autofunction:: huntserver.staff_views.progress(request)
.. autofunction:: huntserver.staff_views.charts(request)
.. autofunction:: huntserver.staff_views.admin_chat(request)
.. autofunction:: huntserver.staff_views.hunt_management(request)
.. autofunction:: huntserver.staff_views.control(request)
.. autofunction:: huntserver.staff_views.emails(request)
.. autofunction:: huntserver.staff_views.depgraph(request)

Auth Views
==========

.. autofunction:: huntserver.auth_views.login_selection(request)
.. autofunction:: huntserver.auth_views.create_account(request)
.. autofunction:: huntserver.auth_views.account_logout(request)
.. autofunction:: huntserver.auth_views.shib_login(request)
