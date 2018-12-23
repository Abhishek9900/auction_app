def post_list(request):
    queryset_list = Profile.objects.active()
    if request.user.is_staff or request.user.is_superuser:
        queryset_list = Profile.objects.all()
    query = request.GET.get("q")
    if query:
        queryset_list = queryset_list.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(designation__icontains=query)
                ).distinct()
    paginator = Paginator(queryset_list, 6)
    page_request_var = "page"
    page = request.GET.get(page_request_var)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        queryset = paginator.page(1)
    except EmptyPage:
        queryset = paginator.page(paginator.num_pages)

    context = {
        "posts": queryset,
        "page_request_var": page_request_var,
    }
    return render(request, 'accounts/post_list.html', context)