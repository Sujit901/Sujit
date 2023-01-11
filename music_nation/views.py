import music_nation
from django.shortcuts import (
    render,
    get_object_or_404,
    redirect
)
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils import timezone
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django import forms

from .forms import SignUpForm
from .models import Album, Song
from .forms import NewAlbum, NewSong
from django.views.generic.list import ListView
##########################################################


def home(request):
    # show all albums in chronological order of it's upload
    albums = Album.objects.all()
    return render(request, 'music_nation/homepage.html', {'albums': albums})

#........................................................#

def profile_detail(request, username):
    # show all albums of the artist
    albums = get_object_or_404(User, username=username) 
    albums = albums.albums.all()
    user = User.objects.get(username=username)
    return render(request, 'music_nation/artist_information.html', {'albums': albums, 'username': username, 'user':user})

#........................................................#


@login_required
def add_album(request, username):
    user = get_object_or_404(User, username=username)
    # only currently logged in user can add album else will be redirected to home
    if user == request.user:
        if request.method == 'POST':
            form = NewAlbum(request.POST, request.FILES)
            if form.is_valid():
                # form.save(commit='False')
                album = Album.objects.create(
                    album_logo=form.cleaned_data.get('album_logo'),
                    album_name=form.cleaned_data.get('album_name'),
                    album_genre=form.cleaned_data.get('album_genre'),
                    uploaded_on=timezone.now(),
                    album_artist=request.user
                )
                return redirect('music_nation:profile_detail', username=request.user)
        else:
            form = NewAlbum()
        return render(request, 'music_nation/create_new_album.html', {'form': form})
    else:
        return redirect('music_nation:profile_detail', username=user)

#........................................................#


def album_detail(request, username, album):
    # show album details here. single album's details.
    album = get_object_or_404(Album, album_name=album)
    songs = get_object_or_404(User, username=username)
    songs = songs.albums.get(album_name=str(album))
    songs = songs.songs.all()
    return render(request, 'music_nation/album_information.html', {'songs': songs, 'album': album, 'username': username
                                                                   })

#........................................................#


def signup(request):

    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('music_nation:home')
        else:
            message = 'Looks like a username with that email or Username already exists'
            return render(request, 'music_nation/user_signup.html', {'form': form, 'message': message})
    else:
        form = SignUpForm()
        return render(request, 'music_nation/user_signup.html', {'form': form})

#........................................................#


@login_required
def delete_album(request, username, album):
    user = get_object_or_404(User, username=username)
    if request.user == user:
        album_to_delete = get_object_or_404(User, username=username)
        album_to_delete = album_to_delete.albums.get(album_name=album)
        song_to_delete = album_to_delete.songs.all()
        for song in song_to_delete:
            song.delete_media()  # deletes the song_file
        album_to_delete.delete_media()  # deletes the album_logo
        album_to_delete.delete()  # deletes the album from database
        return redirect('music_nation:profile_detail', username=username)
    else:
        return redirect('music_nation:profile_detail', username=username)

#........................................................#


@login_required
def add_song(request, username, album):

    user = get_object_or_404(User, username=username)

    if request.user == user:

        album_get = Album.objects.get(album_name=album)

        if request.method == 'POST':
            form = NewSong(request.POST, request.FILES)
            if form.is_valid():
                # form.save(commit='False')
                song = Song.objects.create(
                    song_name=form.cleaned_data.get('song_name'),
                    song_file=form.cleaned_data.get('song_file'),
                    song_album=album_get
                )
                return redirect('music_nation:album_detail', username=username, album=album)

        else:
            form = NewSong()
            return render(request, 'music_nation/create_new_song.html', {'form': form})
    else:
        return redirect('music_nation:album_detail', username=username, album=album)


# views of about us
def AboutView(request):
    return render(request, "music_nation/aboutus.html")

# views of search


class SearchView(ListView):
    model = Song
    template_name = 'music_nation/base.html'
    context_object_name = 'posts'

    def get_queryset(self):
        query = self.request.GET.get('m')
        return Song.objects.filter(song_name__icontains=query)

    
    #password reset
def homepage(request):
    	return render (request=request, template_name="music_nation/base.html")

def password_reset_request(request):
	if request.method == "POST":
		password_reset_form = PasswordResetForm(request.POST)
		if password_reset_form.is_valid():
			data = password_reset_form.cleaned_data['email']
			associated_users = User.objects.filter(Q(email=data))
			if associated_users.exists():
				for user in associated_users:
					subject = "Password Reset Requested"
					email_template_name = "music_nation/password/password_reset_email.txt"
					c = {
					"email":user.email,
					'domain':'127.0.0.1:8000',
					'site_name': 'Website',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					'token': default_token_generator.make_token(user),
					'protocol': 'http',
					}
					email = render_to_string(email_template_name, c)
					try:
						send_mail(subject, email, 'admin@example.com' , [user.email], fail_silently=False)
					except BadHeaderError:

						return HttpResponse('Invalid header found.')
						
					messages.success(request, 'A message with reset password instructions has been sent to your inbox.')
					return redirect ("/password_reset/done/")
			messages.error(request, 'An invalid email has been entered.')
	password_reset_form = PasswordResetForm()
	return render(request=request, template_name="music_nation/password/password_reset.html", context={"password_reset_form":password_reset_form})


#def delete_song(request, username, song):
    #user = get_object_or_404(User, username=username)
    #song_to_delete = get_object_or_404(Song, username=username)
    #song_to_delete = song_to_delete.objects.songs.get(song_name=song)
    #if request.user == user:
            #song.delete_media()
    #return redirect('music_nation:profile_detail', username=username)
